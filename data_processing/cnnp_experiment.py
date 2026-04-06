from __future__ import annotations

import csv
from pathlib import Path


DEFAULT_MODES = ["histogram_shifting", "expansion_embedding"]
DEFAULT_PAYLOADS = [10000, 20000, 50000, 100000]
DEFAULT_IMAGE_SIZE = (512, 512)
DEFAULT_RESULTS_CSV = Path(r"D:\word\tmp\cnnp_results\cnnp_psnr_results.csv")
DEFAULT_PER_IMAGE_CSV = Path(r"D:\word\tmp\cnnp_assets\per_image_results.csv")
DEFAULT_AVERAGE_CSV = Path(r"D:\word\tmp\cnnp_assets\average_results.csv")
DEFAULT_TREND_CSV = Path(r"D:\word\tmp\cnnp_assets\payload_psnr_trend.csv")
DEFAULT_GAP_CSV = Path(r"D:\word\tmp\cnnp_assets\mode_gap_comparison.csv")
DEFAULT_ENV_INFO = Path(r"D:\word\tmp\cnnp_assets\environment_info.txt")
DEFAULT_LOGS_DIR = Path(r"D:\word\tmp\cnnp_results\logs")


def build_conditions(modes, payloads, images):
    conditions = []
    for mode in modes:
        for payload in payloads:
            for image in images:
                conditions.append({"mode": mode, "payload": payload, "image": image})
    return conditions


def summarize_results(rows):
    grouped = {}
    for row in rows:
        key = (row["mode"], int(row["payload"]))
        grouped.setdefault(key, []).append(row)

    summary_rows = []
    for mode, payload in sorted(grouped.keys(), key=lambda item: (item[1], item[0])):
        members = grouped[(mode, payload)]
        summary_rows.append(
            {
                "mode": mode,
                "payload": payload,
                "average_psnr": round(sum(item["psnr"] for item in members) / len(members), 2),
                "average_ssim": round(sum(item["ssim"] for item in members) / len(members), 6),
                "average_elapsed_seconds": round(
                    sum(item["elapsed_seconds"] for item in members) / len(members), 4
                ),
                "image_count": len(members),
            }
        )
    return summary_rows


def build_chart_rows(summary_rows):
    trend_rows = []
    grouped_by_payload = {}

    for row in sorted(summary_rows, key=lambda item: (int(item["payload"]), item["mode"])):
        trend_rows.append(
            {
                "payload": int(row["payload"]),
                "mode": row["mode"],
                "average_psnr": float(row["average_psnr"]),
                "average_ssim": float(row.get("average_ssim", 0.0)),
                "average_elapsed_seconds": float(row.get("average_elapsed_seconds", 0.0)),
            }
        )
        grouped_by_payload.setdefault(int(row["payload"]), {})[row["mode"]] = float(row["average_psnr"])

    gap_rows = []
    for payload in sorted(grouped_by_payload):
        payload_rows = grouped_by_payload[payload]
        hs_psnr = payload_rows.get("histogram_shifting")
        ee_psnr = payload_rows.get("expansion_embedding")
        if hs_psnr is None or ee_psnr is None:
            continue
        gap_rows.append(
            {
                "payload": payload,
                "histogram_shifting_psnr": hs_psnr,
                "expansion_embedding_psnr": ee_psnr,
                "psnr_gap": round(hs_psnr - ee_psnr, 2),
            }
        )

    return trend_rows, gap_rows


def format_environment_lines(env_info):
    return [
        f"run_datetime: {env_info['run_datetime']}",
        f"device: {env_info['device']}",
        f"python_version: {env_info['python_version']}",
        f"torch_version: {env_info['torch_version']}",
        f"matlab_version: {env_info['matlab_version']}",
        f"model_file: {env_info['model_file']}",
        f"image_names: {', '.join(env_info['image_names'])}",
        f"payloads: {', '.join(str(item) for item in env_info['payloads'])}",
        f"modes: {', '.join(env_info['modes'])}",
        f"seed: {env_info['seed']}",
    ]


def write_csv_rows(path, rows):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"cannot write empty csv: {target}")
    with target.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_text_lines(path, lines):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_csv_rows(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))
