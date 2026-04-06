from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_processing.cnnp_experiment import (
    DEFAULT_GAP_CSV,
    DEFAULT_TREND_CSV,
    read_csv_rows,
)


def parse_args():
    parser = argparse.ArgumentParser(description="根据 CNNP 图表源数据生成论文插图")
    parser.add_argument("--trend-csv", default=str(DEFAULT_TREND_CSV), help="折线图源数据 CSV")
    parser.add_argument("--gap-csv", default=str(DEFAULT_GAP_CSV), help="柱状图源数据 CSV")
    parser.add_argument("--trend-png", default=r"D:\word\tmp\cnnp_assets\payload_psnr_trend.png", help="折线图 PNG 输出路径")
    parser.add_argument("--gap-png", default=r"D:\word\tmp\cnnp_assets\mode_gap_comparison.png", help="柱状图 PNG 输出路径")
    return parser.parse_args()


def _load_matplotlib():
    try:
        pyplot = importlib.import_module("matplotlib.pyplot")
    except Exception as exc:
        raise SystemExit("未安装 matplotlib，无法生成 PNG。请先执行: python -m pip install matplotlib") from exc
    return pyplot


def _save_trend_plot(plt, trend_rows, output_path):
    grouped = {}
    for row in trend_rows:
        grouped.setdefault(row["mode"], []).append((int(row["payload"]), float(row["average_psnr"])))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    for mode, values in grouped.items():
        values.sort(key=lambda item: item[0])
        plt.plot([item[0] for item in values], [item[1] for item in values], marker="o", label=mode)
    plt.xlabel("Payload")
    plt.ylabel("Average PSNR")
    plt.title("CNNP Average PSNR vs Payload")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def _save_gap_plot(plt, gap_rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payloads = [int(row["payload"]) for row in gap_rows]
    gaps = [float(row["psnr_gap"]) for row in gap_rows]
    plt.figure(figsize=(8, 5))
    plt.bar(payloads, gaps, width=9000)
    plt.xlabel("Payload")
    plt.ylabel("PSNR Gap (HS - EE)")
    plt.title("Mode Gap Comparison")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def main():
    args = parse_args()
    plt = _load_matplotlib()
    trend_rows = read_csv_rows(args.trend_csv)
    gap_rows = read_csv_rows(args.gap_csv)
    _save_trend_plot(plt, trend_rows, Path(args.trend_png))
    _save_gap_plot(plt, gap_rows, Path(args.gap_png))


if __name__ == "__main__":
    main()
