from __future__ import annotations

import traceback
from dataclasses import dataclass
from pathlib import Path
from queue import Queue
from threading import Event, Thread
from typing import Any

from expansion_closed_loop import (
    build_roundtrip_result,
    embed_secret_text,
    extract_secret_text,
    verify_closed_loop,
    write_roundtrip_report,
)
from gui.config import GuiClosedLoopConfig, GuiExperimentConfig, build_run_output_paths, to_closed_loop_kwargs, to_runtime_kwargs


@dataclass(frozen=True)
class WorkerEvent:
    kind: str
    message: str = ""
    payload: Any = None


class PauseController:
    def __init__(self) -> None:
        self._resume_event = Event()
        self._resume_event.set()

    @property
    def is_paused(self) -> bool:
        return not self._resume_event.is_set()

    def pause(self) -> None:
        self._resume_event.clear()

    def resume(self) -> None:
        self._resume_event.set()

    def wait_if_paused(self) -> None:
        self._resume_event.wait()


def start_experiment_worker(
    config: GuiExperimentConfig,
    events: Queue[WorkerEvent],
    pause_controller: PauseController | None = None,
) -> Thread:
    thread = Thread(target=_run_experiment, args=(config, events, pause_controller), daemon=True)
    thread.start()
    return thread


def start_closed_loop_worker(
    config: GuiClosedLoopConfig,
    events: Queue[WorkerEvent],
    pause_controller: PauseController | None = None,
) -> Thread:
    thread = Thread(target=_run_closed_loop, args=(config, events, pause_controller), daemon=True)
    thread.start()
    return thread


def _wait_if_paused(pause_controller: PauseController | None) -> None:
    if pause_controller is not None:
        pause_controller.wait_if_paused()


def _wrap_seed_progress(progress_callback, seed: int, seed_index: int, seed_count: int):
    local_total_state = {"value": 0}

    def publish(payload):
        event = dict(payload)
        local_total = int(event.get("total", 0) or local_total_state["value"])
        local_current = int(event.get("current", 0) or 0)
        if local_total:
            local_total_state["value"] = local_total
            event["current"] = seed_index * local_total + local_current
            event["total"] = local_total * seed_count
        event["seed"] = seed
        event["seed_index"] = seed_index + 1
        event["seed_count"] = seed_count
        if event.get("stage") == "start":
            event["stage"] = "seed_start"
        elif event.get("stage") == "complete":
            event["stage"] = "seed_complete"
        progress_callback(event)

    return publish


def _normalize_aggregate_rows(rows):
    normalized = []
    for row in rows:
        normalized.append(
            {
                "mode": row["mode"],
                "payload": row["payload"],
                "average_psnr": row["mean_psnr"],
                "std_psnr": row["std_psnr"],
                "psnr_mean_std": row["psnr_mean_std"],
                "average_ssim": row["mean_ssim"],
                "std_ssim": row["std_ssim"],
                "ssim_mean_std": row["ssim_mean_std"],
                "average_elapsed_seconds": row["mean_elapsed_seconds"],
                "std_elapsed_seconds": row["std_elapsed_seconds"],
                "seed_count": row["seed_count"],
                "image_count": row["image_count"],
                "sample_count": row["sample_count"],
            }
        )
    return normalized


def _write_optional_csv(write_csv_rows, path: Path, rows) -> None:
    if rows:
        write_csv_rows(path, rows)


def _write_multi_seed_outputs(config: GuiExperimentConfig, per_image_rows, seed_csv_paths):
    from data_processing.aggregate_multi_seed_results import aggregate_by_image, aggregate_by_mode_payload, build_seed_summary
    from data_processing.cnnp_experiment import build_chart_rows, write_csv_rows

    aggregate_rows = aggregate_by_mode_payload(per_image_rows)
    image_rows = aggregate_by_image(per_image_rows)
    seed_rows = build_seed_summary(seed_csv_paths)
    summary_rows = _normalize_aggregate_rows(aggregate_rows)
    paths = build_run_output_paths(config.output_dir)
    aggregated_dir = config.output_dir / "aggregated"

    write_csv_rows(paths["results_csv_path"], per_image_rows)
    write_csv_rows(paths["per_image_csv_path"], per_image_rows)
    write_csv_rows(paths["average_csv_path"], summary_rows)
    trend_rows, gap_rows = build_chart_rows(summary_rows)
    _write_optional_csv(write_csv_rows, paths["trend_csv_path"], trend_rows)
    _write_optional_csv(write_csv_rows, paths["gap_csv_path"], gap_rows)
    write_csv_rows(aggregated_dir / "mode_payload_summary.csv", aggregate_rows)
    write_csv_rows(aggregated_dir / "mode_payload_image_summary.csv", image_rows)
    write_csv_rows(aggregated_dir / "seed_sources.csv", seed_rows)
    return {
        "per_image_rows": per_image_rows,
        "summary_rows": summary_rows,
        "aggregate_rows": aggregate_rows,
        "image_rows": image_rows,
        "seed_rows": seed_rows,
    }


def _run_configured_experiment(config: GuiExperimentConfig, runner, progress_callback, pause_callback):
    if len(config.seeds) == 1:
        kwargs = to_runtime_kwargs(config, seed=config.seed)
        kwargs["progress_callback"] = progress_callback
        kwargs["pause_callback"] = pause_callback
        return runner(**kwargs)

    all_rows = []
    seed_csv_paths = []
    for seed_index, seed in enumerate(config.seeds):
        seed_dir = config.output_dir / f"seed_{seed}"
        kwargs = to_runtime_kwargs(config, seed=seed, output_dir=seed_dir)
        kwargs["progress_callback"] = _wrap_seed_progress(progress_callback, seed, seed_index, len(config.seeds))
        kwargs["pause_callback"] = pause_callback
        result = runner(**kwargs)
        all_rows.extend(result.get("per_image_rows", []))
        seed_csv_paths.append(kwargs["per_image_csv_path"])

    progress_callback(
        {
            "stage": "complete",
            "current": len(all_rows),
            "total": len(all_rows),
            "output_dir": str(config.output_dir),
        }
    )
    return _write_multi_seed_outputs(config, all_rows, seed_csv_paths)


def _run_experiment(
    config: GuiExperimentConfig,
    events: Queue[WorkerEvent],
    pause_controller: PauseController | None = None,
) -> None:
    try:
        events.put(WorkerEvent("log", f"输出目录：{config.output_dir}"))
        events.put(WorkerEvent("log", "正在加载 CNNP 运行环境和 MATLAB 引擎..."))
        from data_processing.cnnp_runtime import run_batch_experiment

        def publish_progress(payload):
            events.put(WorkerEvent("progress", payload=payload))

        events.put(WorkerEvent("log", "性能评估开始运行，耗时取决于图像数量和载荷长度。"))
        if len(config.seeds) > 1:
            seed_text = ", ".join(str(seed) for seed in config.seeds)
            events.put(WorkerEvent("log", f"多随机种子模式：{seed_text}"))
        result = _run_configured_experiment(
            config,
            run_batch_experiment,
            publish_progress,
            pause_controller.wait_if_paused if pause_controller is not None else None,
        )
        events.put(WorkerEvent("done", "性能评估运行完成。", result))
    except Exception as exc:
        events.put(WorkerEvent("error", str(exc), traceback.format_exc()))


def _run_closed_loop(
    config: GuiClosedLoopConfig,
    events: Queue[WorkerEvent],
    pause_controller: PauseController | None = None,
) -> None:
    try:
        kwargs = to_closed_loop_kwargs(config)
        events.put(WorkerEvent("log", f"闭环输出目录：{config.output_dir}"))
        events.put(WorkerEvent("log", "开始扩展嵌入，正在启动 CNNP 和 MATLAB 引擎..."))
        events.put(WorkerEvent("progress", payload={"stage": "closed_loop_start", "current": 0, "total": 4}))
        _wait_if_paused(pause_controller)
        embed_result = embed_secret_text(
            carrier_path=kwargs["carrier_path"],
            secret_text=kwargs["secret_text"],
            watermarked_path=kwargs["watermarked_path"],
            carrier_output_path=kwargs["carrier_output_path"],
            model_path=kwargs["model_path"],
            image_size=kwargs["image_size"],
        )
        events.put(WorkerEvent("progress", payload={"stage": "closed_loop_embed_done", "current": 1, "total": 4}))
        events.put(WorkerEvent("log", "含密图已生成，开始读取含密图并提取秘密信息..."))
        _wait_if_paused(pause_controller)
        extract_result = extract_secret_text(
            watermarked_path=kwargs["watermarked_path"],
            recovered_path=kwargs["recovered_path"],
            text_output_path=kwargs["text_output_path"],
            bits_output_path=kwargs["bits_output_path"],
            model_path=kwargs["model_path"],
        )
        events.put(WorkerEvent("progress", payload={"stage": "closed_loop_extract_done", "current": 2, "total": 4}))
        events.put(WorkerEvent("log", "提取和恢复完成，开始验证消息与图像一致性..."))
        _wait_if_paused(pause_controller)
        verify_result = verify_closed_loop(
            carrier_path=kwargs["carrier_output_path"],
            recovered_path=kwargs["recovered_path"],
            original_secret_text=kwargs["secret_text"],
            extracted_secret_text=extract_result["secret_text"],
            image_size=kwargs["image_size"],
        )
        events.put(WorkerEvent("progress", payload={"stage": "closed_loop_verify_done", "current": 4, "total": 4}))
        paths = {key: str(value) for key, value in kwargs.items() if key.endswith("_path")}
        roundtrip_result = build_roundtrip_result(
            kwargs["secret_text"],
            embed_result,
            extract_result,
            verify_result,
            paths,
        )
        write_roundtrip_report(kwargs["summary_path"], kwargs["report_path"], roundtrip_result)
        payload = {
            "embed_result": embed_result,
            "extract_result": extract_result,
            "verify_result": verify_result,
            "roundtrip_result": roundtrip_result,
            "paths": paths,
        }
        events.put(WorkerEvent("done", "扩展嵌入闭环运行完成。", payload))
    except Exception as exc:
        events.put(WorkerEvent("error", str(exc), traceback.format_exc()))
