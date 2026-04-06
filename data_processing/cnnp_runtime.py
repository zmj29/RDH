from __future__ import annotations

import importlib
import math
import platform
import time
from datetime import datetime
from pathlib import Path

from data_processing.cnnp_experiment import (
    DEFAULT_ENV_INFO,
    DEFAULT_GAP_CSV,
    DEFAULT_IMAGE_SIZE,
    DEFAULT_LOGS_DIR,
    DEFAULT_MODES,
    DEFAULT_PAYLOADS,
    DEFAULT_PER_IMAGE_CSV,
    DEFAULT_RESULTS_CSV,
    DEFAULT_AVERAGE_CSV,
    DEFAULT_TREND_CSV,
    build_chart_rows,
    format_environment_lines,
    summarize_results,
    write_csv_rows,
    write_text_lines,
)


def _load_runtime_dependencies():
    try:
        cv2 = importlib.import_module("cv2")
        np_module = importlib.import_module("numpy")
        torch = importlib.import_module("torch")
        matlab_engine = importlib.import_module("matlab.engine")
        utils = importlib.import_module("utils")
        predict_model = importlib.import_module("model.predict_model")
    except Exception as exc:
        raise RuntimeError(
            "运行批量实验前，请在兼容环境中安装 torch、torchvision、opencv-python、numpy 和 matlab.engine。"
        ) from exc
    return cv2, np_module, torch, matlab_engine, utils, predict_model.PredictModel


def _build_message(np_module, payload, seed):
    return np_module.random.RandomState(seed).randint(0, 2, payload)


def _calculate_psnr(np_module, embedded_image, original_image):
    mse = np_module.mean((embedded_image.astype(np_module.float64) - original_image.astype(np_module.float64)) ** 2)
    if mse < 1.0e-10:
        return 100.0
    return 10 * math.log10(255.0 ** 2 / float(mse))


def _calculate_ssim(np_module, embedded_image, original_image):
    first = embedded_image.astype(np_module.float64)
    second = original_image.astype(np_module.float64)
    mean_first = float(first.mean())
    mean_second = float(second.mean())
    variance_first = float(((first - mean_first) ** 2).mean())
    variance_second = float(((second - mean_second) ** 2).mean())
    covariance = float(((first - mean_first) * (second - mean_second)).mean())
    constant_one = (0.01 * 255.0) ** 2
    constant_two = (0.03 * 255.0) ** 2
    numerator = (2 * mean_first * mean_second + constant_one) * (2 * covariance + constant_two)
    denominator = (mean_first ** 2 + mean_second ** 2 + constant_one) * (variance_first + variance_second + constant_two)
    return 1.0 if denominator == 0 else numerator / denominator


def _run_single_image(context, image_path, mode, message_bits, image_size):
    image = context["cv2"].imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"无法读取图像: {image_path}")
    resized_image = context["cv2"].resize(image, image_size, interpolation=context["cv2"].INTER_CUBIC)
    gray_image = context["cv2"].cvtColor(resized_image, context["cv2"].COLOR_BGR2GRAY)
    gray_image = context["np"].array(gray_image, dtype=context["np"].float64)
    if mode == "histogram_shifting":
        embedded_image = context["utils"].cnn_histogram_shifting(gray_image, message_bits, context["device"], context["model"], context["engine"])
    elif mode == "expansion_embedding":
        embedded_image = context["utils"].cnn_expansion(gray_image, message_bits, context["device"], context["model"], context["engine"])
    else:
        raise ValueError(f"unsupported mode: {mode}")
    return gray_image, context["np"].array(embedded_image, dtype=context["np"].float64)


def _build_environment_info(context, run_datetime, image_names, payloads, modes, seed):
    return {
        "run_datetime": run_datetime,
        "device": context["device_label"],
        "python_version": platform.python_version(),
        "torch_version": getattr(context["torch"], "__version__", "unknown"),
        "matlab_version": str(context["engine"].version()),
        "model_file": context["model_path"].name,
        "image_names": image_names,
        "payloads": payloads,
        "modes": modes,
        "seed": seed,
    }


def _run_condition(context, image_dir, image_names, mode, payload, seed, image_size, run_datetime):
    rows = []
    log_lines = [
        f"run_datetime: {run_datetime}",
        f"mode: {mode}",
        f"payload: {payload}",
        f"seed: {seed}",
        f"device: {context['device_label']}",
        f"model_file: {context['model_path'].name}",
    ]
    message_bits = _build_message(context["np"], payload, seed)
    for image_name in image_names:
        start_time = time.perf_counter()
        original_image, embedded_image = _run_single_image(context, image_dir / image_name, mode, message_bits, image_size)
        elapsed_seconds = round(time.perf_counter() - start_time, 4)
        row = {
            "mode": mode,
            "payload": payload,
            "image": image_name,
            "psnr": round(_calculate_psnr(context["np"], embedded_image, original_image), 2),
            "ssim": round(_calculate_ssim(context["np"], embedded_image, original_image), 6),
            "elapsed_seconds": elapsed_seconds,
            "run_datetime": run_datetime,
            "device": context["device_label"],
            "model_file": context["model_path"].name,
            "seed": seed,
        }
        rows.append(row)
        log_lines.append(f"image: {image_name}, psnr: {row['psnr']}, ssim: {row['ssim']}, elapsed_seconds: {elapsed_seconds}")
    summary_row = summarize_results(rows)[0]
    log_lines.extend(
        [
            f"average_psnr: {summary_row['average_psnr']}",
            f"average_ssim: {summary_row['average_ssim']}",
            f"average_elapsed_seconds: {summary_row['average_elapsed_seconds']}",
        ]
    )
    return rows, log_lines


def _create_runtime_context(model_path):
    cv2, np_module, torch, matlab_engine, utils, PredictModel = _load_runtime_dependencies()
    project_root = Path(__file__).resolve().parents[1]
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    engine = matlab_engine.start_matlab()
    engine.addpath(str(project_root), nargout=0)
    model = PredictModel(device)
    utils.load_model(str(model_path), model)
    return {
        "cv2": cv2,
        "np": np_module,
        "torch": torch,
        "utils": utils,
        "engine": engine,
        "device": device,
        "device_label": "gpu" if torch.cuda.is_available() else "cpu",
        "model": model,
        "model_path": model_path,
    }


def _write_outputs(per_image_rows, environment_info, results_csv_path, per_image_csv_path, average_csv_path, trend_csv_path, gap_csv_path, environment_info_path):
    summary_rows = summarize_results(per_image_rows)
    trend_rows, gap_rows = build_chart_rows(summary_rows)
    write_csv_rows(results_csv_path, per_image_rows)
    write_csv_rows(per_image_csv_path, per_image_rows)
    write_csv_rows(average_csv_path, summary_rows)
    write_csv_rows(trend_csv_path, trend_rows)
    write_csv_rows(gap_csv_path, gap_rows)
    write_text_lines(environment_info_path, format_environment_lines(environment_info))
    return summary_rows, trend_rows, gap_rows


def run_batch_experiment(
    image_dir,
    model_path,
    modes=None,
    payloads=None,
    seed=20260406,
    image_size=DEFAULT_IMAGE_SIZE,
    results_csv_path=DEFAULT_RESULTS_CSV,
    per_image_csv_path=DEFAULT_PER_IMAGE_CSV,
    average_csv_path=DEFAULT_AVERAGE_CSV,
    trend_csv_path=DEFAULT_TREND_CSV,
    gap_csv_path=DEFAULT_GAP_CSV,
    environment_info_path=DEFAULT_ENV_INFO,
    logs_dir=DEFAULT_LOGS_DIR,
):
    image_dir = Path(image_dir)
    model_path = Path(model_path)
    if not image_dir.exists():
        raise FileNotFoundError(f"image directory not found: {image_dir}")
    if not model_path.exists():
        raise FileNotFoundError(f"model file not found: {model_path}")
    modes = list(modes or DEFAULT_MODES)
    payloads = [int(item) for item in (payloads or DEFAULT_PAYLOADS)]
    image_names = sorted(path.name for path in image_dir.iterdir() if path.is_file())
    if not image_names:
        raise ValueError(f"no images found in: {image_dir}")

    run_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context = _create_runtime_context(model_path)
    per_image_rows = []
    try:
        environment_info = _build_environment_info(context, run_datetime, image_names, payloads, modes, seed)
        for mode in modes:
            for payload in payloads:
                rows, log_lines = _run_condition(context, image_dir, image_names, mode, payload, seed, image_size, run_datetime)
                per_image_rows.extend(rows)
                write_text_lines(Path(logs_dir) / f"{mode}_{payload}.txt", log_lines)
    finally:
        context["engine"].exit()

    summary_rows, trend_rows, gap_rows = _write_outputs(
        per_image_rows,
        environment_info,
        results_csv_path,
        per_image_csv_path,
        average_csv_path,
        trend_csv_path,
        gap_csv_path,
        environment_info_path,
    )
    return {"per_image_rows": per_image_rows, "summary_rows": summary_rows, "trend_rows": trend_rows, "gap_rows": gap_rows}
