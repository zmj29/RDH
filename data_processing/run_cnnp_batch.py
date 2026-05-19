from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_processing.cnnp_experiment import (
    DEFAULT_AVERAGE_CSV,
    DEFAULT_ENV_INFO,
    DEFAULT_GAP_CSV,
    DEFAULT_LOGS_DIR,
    DEFAULT_MODES,
    DEFAULT_PAYLOADS,
    DEFAULT_PER_IMAGE_CSV,
    DEFAULT_RESULTS_CSV,
    DEFAULT_TREND_CSV,
)
from data_processing.cnnp_runtime import run_batch_experiment


def parse_args():
    parser = argparse.ArgumentParser(description="批量运行 CNNP 论文实验并导出 CSV 与日志")
    parser.add_argument("--image-dir", default=r".\datasets\standard_test_images", help="标准测试图像目录")
    parser.add_argument("--model-path", default=r".\model_parameter\model_state.pth", help="模型权重路径")
    parser.add_argument("--modes", nargs="+", default=DEFAULT_MODES, help="实验模式列表")
    parser.add_argument("--payloads", nargs="+", default=DEFAULT_PAYLOADS, type=int, help="载荷列表")
    parser.add_argument("--seed", default=20260406, type=int, help="固定随机种子")
    parser.add_argument("--results-csv", default=str(DEFAULT_RESULTS_CSV), help="详细结果 CSV 输出路径")
    parser.add_argument("--per-image-csv", default=str(DEFAULT_PER_IMAGE_CSV), help="逐图像结果 CSV 输出路径")
    parser.add_argument("--average-csv", default=str(DEFAULT_AVERAGE_CSV), help="平均结果 CSV 输出路径")
    parser.add_argument("--trend-csv", default=str(DEFAULT_TREND_CSV), help="图 5.1 源数据 CSV 输出路径")
    parser.add_argument("--gap-csv", default=str(DEFAULT_GAP_CSV), help="图 5.2 源数据 CSV 输出路径")
    parser.add_argument("--env-info", default=str(DEFAULT_ENV_INFO), help="环境说明文本输出路径")
    parser.add_argument("--logs-dir", default=str(DEFAULT_LOGS_DIR), help="原始日志目录")
    return parser.parse_args()


def main():
    args = parse_args()
    run_batch_experiment(
        image_dir=Path(args.image_dir),
        model_path=Path(args.model_path),
        modes=args.modes,
        payloads=args.payloads,
        seed=args.seed,
        results_csv_path=Path(args.results_csv),
        per_image_csv_path=Path(args.per_image_csv),
        average_csv_path=Path(args.average_csv),
        trend_csv_path=Path(args.trend_csv),
        gap_csv_path=Path(args.gap_csv),
        environment_info_path=Path(args.env_info),
        logs_dir=Path(args.logs_dir),
    )


if __name__ == "__main__":
    main()
