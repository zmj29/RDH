from __future__ import annotations

import argparse
import json
from pathlib import Path

from expansion_closed_loop import (
    DEFAULT_IMAGE_SIZE,
    DEFAULT_MODEL_PATH,
    embed_secret_text,
    extract_secret_text,
    run_expansion_roundtrip,
    verify_closed_loop,
    write_json_summary,
)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if getattr(args, "summary", None):
        write_json_summary(args.summary, result)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="CNNP 扩展嵌入完整闭环工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    embed_parser = subparsers.add_parser("embed", help="嵌入秘密文本并保存含密图")
    embed_parser.add_argument("--carrier", required=True, type=Path, help="载体图像路径")
    _add_secret_input(embed_parser)
    embed_parser.add_argument("--watermarked", required=True, type=Path, help="含密图输出路径，建议使用 PNG 或 BMP")
    embed_parser.add_argument("--carrier-output", type=Path, help="保存实际参与嵌入的灰度载体图")
    embed_parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path, help="CNNP 模型权重路径")
    embed_parser.add_argument("--img-size", nargs=2, default=DEFAULT_IMAGE_SIZE, type=int, metavar=("W", "H"))
    embed_parser.add_argument("--summary", type=Path, help="JSON 摘要输出路径")
    embed_parser.set_defaults(func=_run_embed)

    extract_parser = subparsers.add_parser("extract", help="从含密图提取秘密文本并恢复载体")
    extract_parser.add_argument("--watermarked", required=True, type=Path, help="含密图路径")
    extract_parser.add_argument("--recovered", required=True, type=Path, help="恢复图输出路径")
    extract_parser.add_argument("--text-output", type=Path, help="提取文本输出路径")
    extract_parser.add_argument("--bits-output", type=Path, help="提取比特流输出路径")
    extract_parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path, help="CNNP 模型权重路径")
    extract_parser.add_argument("--summary", type=Path, help="JSON 摘要输出路径")
    extract_parser.set_defaults(func=_run_extract)

    verify_parser = subparsers.add_parser("verify", help="验证秘密文本和恢复图是否一致")
    verify_parser.add_argument("--carrier", required=True, type=Path, help="原始载体图路径")
    verify_parser.add_argument("--recovered", required=True, type=Path, help="恢复图路径")
    _add_secret_input(verify_parser)
    verify_parser.add_argument("--extracted-text", help="提取出的秘密文本")
    verify_parser.add_argument("--extracted-file", type=Path, help="提取文本文件路径")
    verify_parser.add_argument("--img-size", nargs=2, default=DEFAULT_IMAGE_SIZE, type=int, metavar=("W", "H"))
    verify_parser.add_argument("--summary", type=Path, help="JSON 摘要输出路径")
    verify_parser.set_defaults(func=_run_verify)

    roundtrip_parser = subparsers.add_parser("roundtrip", help="一次性完成嵌入、提取、恢复和验证")
    roundtrip_parser.add_argument("--carrier", required=True, type=Path, help="载体图像路径")
    _add_secret_input(roundtrip_parser)
    roundtrip_parser.add_argument("--output-dir", required=True, type=Path, help="闭环输出目录")
    roundtrip_parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path, help="CNNP 模型权重路径")
    roundtrip_parser.add_argument("--img-size", nargs=2, default=DEFAULT_IMAGE_SIZE, type=int, metavar=("W", "H"))
    roundtrip_parser.add_argument("--summary", type=Path, help="额外 JSON 摘要输出路径")
    roundtrip_parser.set_defaults(func=_run_roundtrip)
    return parser


def _add_secret_input(parser):
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--secret-text", help="秘密文本")
    group.add_argument("--secret-file", type=Path, help="秘密文本文件路径")


def _read_secret(args):
    if args.secret_file is not None:
        return args.secret_file.read_text(encoding="utf-8")
    return args.secret_text


def _read_extracted_text(args):
    if args.extracted_file is not None:
        return args.extracted_file.read_text(encoding="utf-8")
    if args.extracted_text is not None:
        return args.extracted_text
    raise ValueError("verify 需要提供 --extracted-text 或 --extracted-file")


def _run_embed(args):
    return embed_secret_text(
        carrier_path=args.carrier,
        secret_text=_read_secret(args),
        watermarked_path=args.watermarked,
        carrier_output_path=args.carrier_output,
        model_path=args.model,
        image_size=tuple(args.img_size),
    )


def _run_extract(args):
    return extract_secret_text(
        watermarked_path=args.watermarked,
        recovered_path=args.recovered,
        text_output_path=args.text_output,
        bits_output_path=args.bits_output,
        model_path=args.model,
    )


def _run_verify(args):
    return verify_closed_loop(
        carrier_path=args.carrier,
        recovered_path=args.recovered,
        original_secret_text=_read_secret(args),
        extracted_secret_text=_read_extracted_text(args),
        image_size=tuple(args.img_size),
    )


def _run_roundtrip(args):
    return run_expansion_roundtrip(
        carrier_path=args.carrier,
        secret_text=_read_secret(args),
        output_dir=args.output_dir,
        model_path=args.model,
        image_size=tuple(args.img_size),
    )


if __name__ == "__main__":
    raise SystemExit(main())
