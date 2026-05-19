from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


RECOMMENDED_IMAGE_SET = [
    "Barbara",
    "Lena",
    "Peppers",
    "yacht",
    "Baboon",
    "Boat",
    "Goldhill",
    "Airplane",
]
SUPPORTED_EXTENSIONS = {".bmp", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}


def get_recommended_image_set():
    return list(RECOMMENDED_IMAGE_SET)


def list_supported_images(input_dir):
    input_dir = Path(input_dir)
    return sorted(
        [
            path
            for path in input_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ],
        key=lambda path: path.name.lower(),
    )


def build_output_path(output_dir, source_path):
    return Path(output_dir) / f"{Path(source_path).stem}.bmp"


def _load_cv2():
    try:
        import cv2  # type: ignore
    except Exception as exc:  # pragma: no cover - runtime diagnostic
        raise RuntimeError(
            "运行图片预处理脚本前，请在实验环境中安装 opencv-python。"
        ) from exc
    return cv2


def convert_image_directory(input_dir, output_dir, size=(512, 512)):
    cv2 = _load_cv2()
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = []
    for source_path in list_supported_images(input_dir):
        image = cv2.imread(str(source_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise FileNotFoundError(f"无法读取图像: {source_path}")
        resized = cv2.resize(image, size, interpolation=cv2.INTER_CUBIC)
        target_path = build_output_path(output_dir, source_path)
        if not cv2.imwrite(str(target_path), resized):
            raise RuntimeError(f"写出失败: {target_path}")
        converted.append(target_path)
    return converted


def parse_args():
    parser = argparse.ArgumentParser(description="批量转换扩样本测试图为 512x512 灰度 BMP")
    parser.add_argument(
        "--input-dir",
        default=r".\datasets\extended_test_images_raw",
        help="原始扩样本图片目录",
    )
    parser.add_argument(
        "--output-dir",
        default=r".\datasets\extended_test_images_8",
        help="输出目录",
    )
    parser.add_argument(
        "--size",
        nargs=2,
        default=[512, 512],
        type=int,
        metavar=("WIDTH", "HEIGHT"),
        help="输出尺寸",
    )
    parser.add_argument(
        "--list-recommended",
        action="store_true",
        help="只打印推荐的 8 张图名单",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list_recommended:
        for name in get_recommended_image_set():
            print(name)
        return

    converted = convert_image_directory(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        size=(args.size[0], args.size[1]),
    )
    print(f"converted={len(converted)}")
    for path in converted:
        print(path)


if __name__ == "__main__":
    main()
