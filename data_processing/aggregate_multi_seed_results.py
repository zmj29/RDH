from __future__ import annotations

import argparse
import re
import statistics
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_processing.cnnp_experiment import read_csv_rows, write_csv_rows


DEFAULT_MULTI_SEED_ROOT = Path(r".\results\multi_seed_8img")
DEFAULT_AGGREGATED_DIR = DEFAULT_MULTI_SEED_ROOT / "aggregated"


def _mean(values):
    return sum(values) / len(values)


def _std(values):
    if len(values) < 2:
        return 0.0
    return statistics.stdev(values)


def _extract_seed(text):
    matches = re.findall(r"seed_(\d+)", str(text))
    return matches[-1] if matches else "unknown"


def build_seed_summary(seed_csv_paths):
    rows = []
    for path in sorted(seed_csv_paths, key=lambda item: _extract_seed(item)):
        rows.append({"seed": _extract_seed(path), "source_csv": str(path)})
    return rows


def aggregate_by_mode_payload(rows):
    grouped = {}
    for row in rows:
        key = (row["mode"], int(row["payload"]))
        grouped.setdefault(key, []).append(row)

    summary_rows = []
    for mode, payload in sorted(grouped.keys(), key=lambda item: (item[1], item[0])):
        members = grouped[(mode, payload)]
        psnr_values = [float(item["psnr"]) for item in members]
        ssim_values = [float(item["ssim"]) for item in members]
        elapsed_values = [float(item["elapsed_seconds"]) for item in members]
        mean_psnr = round(_mean(psnr_values), 2)
        std_psnr = round(_std(psnr_values), 2)
        mean_ssim = round(_mean(ssim_values), 6)
        std_ssim = round(_std(ssim_values), 6)
        mean_elapsed = round(_mean(elapsed_values), 4)
        std_elapsed = round(_std(elapsed_values), 4)
        summary_rows.append(
            {
                "mode": mode,
                "payload": payload,
                "mean_psnr": mean_psnr,
                "std_psnr": std_psnr,
                "psnr_mean_std": f"{mean_psnr:.2f} ± {std_psnr:.2f}",
                "mean_ssim": mean_ssim,
                "std_ssim": std_ssim,
                "ssim_mean_std": f"{mean_ssim:.6f} ± {std_ssim:.6f}",
                "mean_elapsed_seconds": mean_elapsed,
                "std_elapsed_seconds": std_elapsed,
                "elapsed_mean_std": f"{mean_elapsed:.4f} ± {std_elapsed:.4f}",
                "seed_count": len({str(item["seed"]) for item in members}),
                "image_count": len({item["image"] for item in members}),
                "sample_count": len(members),
            }
        )
    return summary_rows


def aggregate_by_image(rows):
    grouped = {}
    for row in rows:
        key = (row["mode"], int(row["payload"]), row["image"])
        grouped.setdefault(key, []).append(row)

    image_rows = []
    for mode, payload, image in sorted(grouped.keys(), key=lambda item: (item[1], item[0], item[2].lower())):
        members = grouped[(mode, payload, image)]
        psnr_values = [float(item["psnr"]) for item in members]
        ssim_values = [float(item["ssim"]) for item in members]
        elapsed_values = [float(item["elapsed_seconds"]) for item in members]
        mean_psnr = round(_mean(psnr_values), 2)
        std_psnr = round(_std(psnr_values), 2)
        mean_ssim = round(_mean(ssim_values), 6)
        std_ssim = round(_std(ssim_values), 6)
        mean_elapsed = round(_mean(elapsed_values), 4)
        std_elapsed = round(_std(elapsed_values), 4)
        image_rows.append(
            {
                "mode": mode,
                "payload": payload,
                "image": image,
                "mean_psnr": mean_psnr,
                "std_psnr": std_psnr,
                "psnr_mean_std": f"{mean_psnr:.2f} ± {std_psnr:.2f}",
                "mean_ssim": mean_ssim,
                "std_ssim": std_ssim,
                "ssim_mean_std": f"{mean_ssim:.6f} ± {std_ssim:.6f}",
                "mean_elapsed_seconds": mean_elapsed,
                "std_elapsed_seconds": std_elapsed,
                "elapsed_mean_std": f"{mean_elapsed:.4f} ± {std_elapsed:.4f}",
                "seed_count": len({str(item["seed"]) for item in members}),
                "sample_count": len(members),
            }
        )
    return image_rows


def discover_seed_csv_files(input_root):
    input_root = Path(input_root)
    return sorted(input_root.glob(r"seed_*\per_image_results.csv"), key=lambda path: _extract_seed(path))


def aggregate_seed_directory(input_root, summary_csv_path, image_csv_path, seed_summary_csv_path):
    seed_csv_paths = discover_seed_csv_files(input_root)
    if not seed_csv_paths:
        raise FileNotFoundError(f"未找到多随机种子结果文件: {input_root}")

    all_rows = []
    for seed_csv_path in seed_csv_paths:
        all_rows.extend(read_csv_rows(seed_csv_path))

    summary_rows = aggregate_by_mode_payload(all_rows)
    image_rows = aggregate_by_image(all_rows)
    seed_summary_rows = build_seed_summary(seed_csv_paths)

    write_csv_rows(summary_csv_path, summary_rows)
    write_csv_rows(image_csv_path, image_rows)
    write_csv_rows(seed_summary_csv_path, seed_summary_rows)
    return summary_rows, image_rows, seed_summary_rows


def parse_args():
    parser = argparse.ArgumentParser(description="聚合多随机种子实验结果并生成 平均值±标准差 表")
    parser.add_argument(
        "--input-root",
        default=str(DEFAULT_MULTI_SEED_ROOT),
        help="包含多个 seed_* 子目录的根目录",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(DEFAULT_AGGREGATED_DIR / "mode_payload_summary.csv"),
        help="按 mode+payload 聚合的输出 CSV",
    )
    parser.add_argument(
        "--image-csv",
        default=str(DEFAULT_AGGREGATED_DIR / "mode_payload_image_summary.csv"),
        help="按 mode+payload+image 聚合的输出 CSV",
    )
    parser.add_argument(
        "--seed-summary-csv",
        default=str(DEFAULT_AGGREGATED_DIR / "seed_sources.csv"),
        help="种子来源清单 CSV",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    summary_rows, image_rows, seed_summary_rows = aggregate_seed_directory(
        input_root=args.input_root,
        summary_csv_path=args.summary_csv,
        image_csv_path=args.image_csv,
        seed_summary_csv_path=args.seed_summary_csv,
    )
    print(f"summary_rows={len(summary_rows)}")
    print(f"image_rows={len(image_rows)}")
    print(f"seed_rows={len(seed_summary_rows)}")


if __name__ == "__main__":
    main()
