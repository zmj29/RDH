from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASETS_DIR = PROJECT_ROOT / "datasets"
DEFAULT_IMAGE_DIR = DATASETS_DIR / "extended_test_images_8"
DEFAULT_CLOSED_LOOP_CARRIER = DATASETS_DIR / "standard_test_images" / "Lena.bmp"
DEFAULT_IMAGE_SIZE = (512, 512)
DEFAULT_OUTPUT_BASE = PROJECT_ROOT / "results" / "gui_runs"
DEFAULT_CLOSED_LOOP_OUTPUT_BASE = PROJECT_ROOT / "results" / "gui_closed_loop"
DEFAULT_PAYLOADS_TEXT = "10000,20000,50000,100000"
DEFAULT_SEEDS_TEXT = "20260406,20260407,20260408"
VALID_MODES = ("histogram_shifting", "expansion_embedding")


@dataclass(frozen=True)
class GuiExperimentConfig:
    image_dir: Path
    model_path: Path
    modes: tuple[str, ...]
    payloads: tuple[int, ...]
    seeds: tuple[int, ...]
    output_dir: Path
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE

    @property
    def seed(self) -> int:
        return self.seeds[0]


@dataclass(frozen=True)
class GuiClosedLoopConfig:
    carrier_path: Path
    model_path: Path
    secret_text: str
    output_dir: Path
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE


def _parse_int_list(raw_value: str, empty_message: str, value_label: str, minimum: int) -> tuple[int, ...]:
    parts = [part for part in re.split(r"[,;\s]+", raw_value.strip()) if part]
    if not parts:
        raise ValueError(empty_message)

    values = []
    for part in parts:
        try:
            value = int(part)
        except ValueError as exc:
            raise ValueError(f"{value_label}必须是整数：{part}") from exc
        if value < minimum:
            raise ValueError(f"{value_label}必须大于或等于 {minimum}：{part}")
        values.append(value)
    return tuple(values)


def parse_payloads(raw_value: str) -> tuple[int, ...]:
    return _parse_int_list(raw_value, "请至少输入一个载荷长度", "载荷长度", 1)


def parse_seeds(raw_value: str) -> tuple[int, ...]:
    return _parse_int_list(raw_value, "请至少输入一个随机种子", "随机种子", 0)


def build_timestamped_output_dir(base_dir: Path | str, now: datetime | None = None) -> Path:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return Path(base_dir) / f"run_{timestamp}"


def build_run_output_paths(output_dir: Path | str) -> dict[str, Path]:
    target = Path(output_dir)
    return {
        "results_csv_path": target / "cnnp_psnr_results.csv",
        "per_image_csv_path": target / "per_image_results.csv",
        "average_csv_path": target / "average_results.csv",
        "trend_csv_path": target / "payload_psnr_trend.csv",
        "gap_csv_path": target / "mode_gap_comparison.csv",
        "environment_info_path": target / "environment_info.txt",
        "logs_dir": target / "logs",
    }


def build_closed_loop_output_paths(output_dir: Path | str) -> dict[str, Path]:
    target = Path(output_dir)
    return {
        "watermarked_path": target / "watermarked.png",
        "carrier_output_path": target / "carrier.png",
        "recovered_path": target / "recovered.png",
        "text_output_path": target / "extracted.txt",
        "bits_output_path": target / "extracted_bits.txt",
        "summary_path": target / "verification_summary.json",
        "report_path": target / "closed_loop_report.txt",
    }


def to_runtime_kwargs(
    config: GuiExperimentConfig,
    seed: int | None = None,
    output_dir: Path | str | None = None,
) -> dict[str, object]:
    selected_output_dir = Path(output_dir) if output_dir is not None else config.output_dir
    kwargs = {
        "image_dir": config.image_dir,
        "model_path": config.model_path,
        "modes": list(config.modes),
        "payloads": list(config.payloads),
        "seed": config.seed if seed is None else seed,
        "image_size": config.image_size,
    }
    kwargs.update(build_run_output_paths(selected_output_dir))
    return kwargs


def to_closed_loop_kwargs(config: GuiClosedLoopConfig) -> dict[str, object]:
    kwargs = {
        "carrier_path": config.carrier_path,
        "model_path": config.model_path,
        "secret_text": config.secret_text,
        "output_dir": config.output_dir,
        "image_size": config.image_size,
    }
    kwargs.update(build_closed_loop_output_paths(config.output_dir))
    return kwargs
