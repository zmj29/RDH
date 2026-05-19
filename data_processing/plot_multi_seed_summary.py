from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_processing.cnnp_experiment import read_csv_rows


DEFAULT_SUMMARY_CSV = PROJECT_ROOT / "results" / "multi_seed_8img" / "aggregated" / "mode_payload_summary.csv"
DEFAULT_OUTPUT_PNG = PROJECT_ROOT / "results" / "multi_seed_8img" / "aggregated" / "payload_psnr_line.png"
DEFAULT_OUTPUT_SVG = PROJECT_ROOT / "results" / "multi_seed_8img" / "aggregated" / "payload_psnr_line.svg"

MODE_LABELS = {
    "expansion_embedding": "扩展嵌入",
    "histogram_shifting": "直方图平移",
}
MODE_COLORS = {
    "expansion_embedding": "#C0504D",
    "histogram_shifting": "#1F4E79",
}
MODE_ORDER = ["expansion_embedding", "histogram_shifting"]


def parse_args():
    parser = argparse.ArgumentParser(description="Generate PSNR-vs-payload line chart.")
    parser.add_argument("--summary-csv", default=str(DEFAULT_SUMMARY_CSV), help="mode_payload_summary.csv path")
    parser.add_argument("--output-png", default=str(DEFAULT_OUTPUT_PNG), help="PNG output path")
    parser.add_argument("--output-svg", default=str(DEFAULT_OUTPUT_SVG), help="SVG output path")
    return parser.parse_args()


def _load_matplotlib():
    try:
        return importlib.import_module("matplotlib.pyplot")
    except Exception as exc:
        raise SystemExit("未安装 matplotlib，无法生成图表。请使用已安装 matplotlib 的 Python 环境运行。") from exc


def _configure_chinese_font(plt):
    font_manager = importlib.import_module("matplotlib.font_manager")
    available = {font.name for font in font_manager.fontManager.ttflist}
    preferred = ["Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC", "Source Han Sans SC"]
    for font_name in preferred:
        if font_name in available:
            plt.rcParams["font.sans-serif"] = [font_name]
            break
    plt.rcParams["axes.unicode_minus"] = False


def _group_rows(rows):
    grouped = {}
    for row in rows:
        mode = row["mode"]
        grouped.setdefault(mode, []).append(
            {
                "payload": int(row["payload"]),
                "mean_psnr": float(row["mean_psnr"]),
            }
        )
    for values in grouped.values():
        values.sort(key=lambda item: item["payload"])
    return grouped


def save_plot(plt, grouped, output_png, output_svg):
    output_png = Path(output_png)
    output_svg = Path(output_svg)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    output_svg.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    all_psnr_values = []
    all_payloads = set()

    for mode in MODE_ORDER:
        values = grouped.get(mode)
        if not values:
            continue
        payloads = [item["payload"] for item in values]
        means = [item["mean_psnr"] for item in values]
        all_payloads.update(payloads)
        all_psnr_values.extend(means)
        ax.plot(
            payloads,
            means,
            color=MODE_COLORS[mode],
            marker="o",
            markersize=5,
            linewidth=2,
            label=MODE_LABELS[mode],
        )

    ax.set_xlabel("嵌入载荷 / bit")
    ax.set_ylabel("平均 PSNR / dB")
    ax.set_xticks(sorted(all_payloads))
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(frameon=False)
    if all_psnr_values:
        ax.set_ylim(max(0, min(all_psnr_values) - 2.0), max(all_psnr_values) + 2.0)
    fig.tight_layout()
    fig.savefig(output_png, dpi=450)
    fig.savefig(output_svg)
    plt.close(fig)


def main():
    args = parse_args()
    plt = _load_matplotlib()
    _configure_chinese_font(plt)
    rows = read_csv_rows(args.summary_csv)
    grouped = _group_rows(rows)
    save_plot(plt, grouped, args.output_png, args.output_svg)
    print(f"saved_png={args.output_png}")
    print(f"saved_svg={args.output_svg}")


if __name__ == "__main__":
    main()
