from __future__ import annotations

import json
from pathlib import Path

from rdh_bits import bits_to_text, ensure_even_bit_count, normalize_bits, text_to_bits


DEFAULT_IMAGE_SIZE = (512, 512)
DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "model_parameter" / "model_state.pth"


def reverse_two_stage(watermarked_image, reverse_stage):
    after_stage_zero, second_half_bits = reverse_stage(watermarked_image, 1)
    carrier_image, first_half_bits = reverse_stage(after_stage_zero, 0)
    return carrier_image, list(first_half_bits) + list(second_half_bits)


def build_verification_result(original_bits, extracted_bits, original_image, recovered_image):
    original_bits = normalize_bits(original_bits)
    extracted_bits = normalize_bits(extracted_bits)
    bit_error_count = _count_sequence_errors(original_bits, extracted_bits)
    original_pixels = list(_flatten(original_image))
    recovered_pixels = list(_flatten(recovered_image))
    pixel_error_count = _count_sequence_errors(original_pixels, recovered_pixels)
    return {
        "message_match": bit_error_count == 0,
        "image_match": pixel_error_count == 0,
        "bit_error_count": bit_error_count,
        "pixel_error_count": pixel_error_count,
        "original_bit_count": len(original_bits),
        "extracted_bit_count": len(extracted_bits),
        "original_pixel_count": len(original_pixels),
        "recovered_pixel_count": len(recovered_pixels),
    }


def embed_secret_text(
    carrier_path,
    secret_text,
    watermarked_path,
    carrier_output_path=None,
    model_path=DEFAULT_MODEL_PATH,
    image_size=DEFAULT_IMAGE_SIZE,
):
    secret_bits = ensure_even_bit_count(text_to_bits(secret_text))
    context = create_runtime_context(model_path)
    try:
        carrier_image = read_carrier_image(carrier_path, image_size)
        embedded_image = context["utils"].cnn_expansion(
            carrier_image,
            context["np"].array(secret_bits, dtype=context["np"].float64),
            context["device"],
            context["model"],
            context["engine"],
        )
        save_gray_image(watermarked_path, embedded_image)
        if carrier_output_path is not None:
            save_gray_image(carrier_output_path, carrier_image)
        return {
            "mode": "expansion_embedding",
            "carrier_path": str(carrier_path),
            "watermarked_path": str(watermarked_path),
            "carrier_output_path": None if carrier_output_path is None else str(carrier_output_path),
            "secret_bit_count": len(secret_bits),
        }
    finally:
        context["engine"].exit()


def extract_secret_text(
    watermarked_path,
    recovered_path,
    text_output_path=None,
    bits_output_path=None,
    model_path=DEFAULT_MODEL_PATH,
):
    context = create_runtime_context(model_path)
    try:
        watermarked_image = read_gray_image(watermarked_path)

        def reverse_stage(image, parity):
            predicted_image = predict_image_for_parity(image, parity, context)
            return matlab_expansion_extract_stage(image, predicted_image, parity, context)

        recovered_image, payload_bits = reverse_two_stage(watermarked_image, reverse_stage)
        secret_text = bits_to_text(payload_bits)
        save_gray_image(recovered_path, recovered_image)
        if text_output_path is not None:
            write_text_file(text_output_path, secret_text, encoding="utf-8")
        if bits_output_path is not None:
            write_text_file(bits_output_path, "".join(str(bit) for bit in payload_bits), encoding="ascii")
        return {
            "mode": "expansion_embedding",
            "watermarked_path": str(watermarked_path),
            "recovered_path": str(recovered_path),
            "text_output_path": None if text_output_path is None else str(text_output_path),
            "bits_output_path": None if bits_output_path is None else str(bits_output_path),
            "secret_text": secret_text,
            "secret_bit_count": len(payload_bits),
        }
    finally:
        context["engine"].exit()


def verify_closed_loop(
    carrier_path,
    recovered_path,
    original_secret_text,
    extracted_secret_text,
    image_size=DEFAULT_IMAGE_SIZE,
):
    original_bits = text_to_bits(original_secret_text)
    extracted_bits = text_to_bits(extracted_secret_text)
    original_image = read_carrier_image(carrier_path, image_size)
    recovered_image = read_gray_image(recovered_path)
    return build_verification_result(original_bits, extracted_bits, original_image, recovered_image)


def build_roundtrip_result(secret_text, embed_result, extract_result, verify_result, paths):
    status = "success" if verify_result.get("message_match") and verify_result.get("image_match") else "failed"
    return {
        "mode": "expansion_embedding",
        "status": status,
        "secret_text": secret_text,
        "extracted_text": extract_result.get("secret_text", ""),
        "embed_result": embed_result,
        "extract_result": extract_result,
        "verify_result": verify_result,
        "paths": {key: str(value) for key, value in paths.items()},
    }


def format_roundtrip_report(result):
    verify_result = result.get("verify_result", {})
    paths = result.get("paths", {})
    lines = [
        "CNNP 扩展嵌入闭环验证报告",
        "",
        f"模式: {result.get('mode')}",
        f"状态: {result.get('status')}",
        f"秘密文本: {result.get('secret_text', '')}",
        f"提取文本: {result.get('extracted_text', '')}",
        f"消息一致: {verify_result.get('message_match')}",
        f"图像一致: {verify_result.get('image_match')}",
        f"bit错误数: {verify_result.get('bit_error_count')}",
        f"像素错误数: {verify_result.get('pixel_error_count')}",
        f"原始bit数: {verify_result.get('original_bit_count')}",
        f"提取bit数: {verify_result.get('extracted_bit_count')}",
        "",
        "输出文件:",
    ]
    for key in (
        "carrier_output_path",
        "watermarked_path",
        "recovered_path",
        "text_output_path",
        "bits_output_path",
        "summary_path",
        "report_path",
    ):
        if paths.get(key):
            lines.append(f"- {key}: {paths[key]}")
    return "\n".join(lines) + "\n"


def write_roundtrip_report(summary_path, report_path, result):
    write_json_summary(summary_path, result)
    write_text_file(report_path, format_roundtrip_report(result), encoding="utf-8")


def run_expansion_roundtrip(
    carrier_path,
    secret_text,
    output_dir,
    model_path=DEFAULT_MODEL_PATH,
    image_size=DEFAULT_IMAGE_SIZE,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "carrier_path": Path(carrier_path),
        "model_path": Path(model_path),
        "watermarked_path": output_dir / "watermarked.png",
        "carrier_output_path": output_dir / "carrier.png",
        "recovered_path": output_dir / "recovered.png",
        "text_output_path": output_dir / "extracted.txt",
        "bits_output_path": output_dir / "extracted_bits.txt",
        "summary_path": output_dir / "verification_summary.json",
        "report_path": output_dir / "closed_loop_report.txt",
    }
    embed_result = embed_secret_text(
        carrier_path=paths["carrier_path"],
        secret_text=secret_text,
        watermarked_path=paths["watermarked_path"],
        carrier_output_path=paths["carrier_output_path"],
        model_path=paths["model_path"],
        image_size=image_size,
    )
    extract_result = extract_secret_text(
        watermarked_path=paths["watermarked_path"],
        recovered_path=paths["recovered_path"],
        text_output_path=paths["text_output_path"],
        bits_output_path=paths["bits_output_path"],
        model_path=paths["model_path"],
    )
    verify_result = verify_closed_loop(
        carrier_path=paths["carrier_output_path"],
        recovered_path=paths["recovered_path"],
        original_secret_text=secret_text,
        extracted_secret_text=extract_result["secret_text"],
        image_size=image_size,
    )
    result = build_roundtrip_result(secret_text, embed_result, extract_result, verify_result, paths)
    write_roundtrip_report(paths["summary_path"], paths["report_path"], result)
    return result


def write_json_summary(path, payload):
    write_text_file(path, json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text_file(path, text, encoding):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding=encoding)


def create_runtime_context(model_path):
    cv2, np_module, torch, matlab_engine, utils, PredictModel = load_runtime_dependencies()
    project_root = Path(__file__).resolve().parent
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    engine = matlab_engine.start_matlab()
    try:
        engine.addpath(str(project_root), nargout=0)
        engine.addpath(str(project_root / "matlab"), nargout=0)
        model = PredictModel(device)
        utils.load_model(str(model_path), model)
    except Exception:
        engine.exit()
        raise
    return {
        "cv2": cv2,
        "np": np_module,
        "torch": torch,
        "utils": utils,
        "engine": engine,
        "device": device,
        "model": model,
    }


def load_runtime_dependencies():
    import importlib

    cv2 = importlib.import_module("cv2")
    np_module = importlib.import_module("numpy")
    torch = importlib.import_module("torch")
    matlab_engine = importlib.import_module("matlab.engine")
    utils = importlib.import_module("utils")
    predict_model = importlib.import_module("model.predict_model")
    return cv2, np_module, torch, matlab_engine, utils, predict_model.PredictModel


def load_image_dependencies():
    import importlib

    return importlib.import_module("cv2"), importlib.import_module("numpy")


def read_carrier_image(path, image_size=DEFAULT_IMAGE_SIZE):
    image = read_gray_image(path)
    if image_size is None:
        return image
    cv2, np_module = load_image_dependencies()
    resized = cv2.resize(image.astype(np_module.uint8), tuple(image_size), interpolation=cv2.INTER_CUBIC)
    return np_module.array(resized, dtype=np_module.float64)


def read_gray_image(path):
    cv2, np_module = load_image_dependencies()
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"无法读取图像: {path}")
    if len(image.shape) == 3:
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np_module.array(image, dtype=np_module.float64)


def save_gray_image(path, image):
    cv2, np_module = load_image_dependencies()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    output = np_module.clip(np_module.rint(image), 0, 255).astype(np_module.uint8)
    if not cv2.imwrite(str(target), output):
        raise OSError(f"无法写入图像: {target}")


def predict_image_for_parity(image, parity, context):
    input_image = context["utils"].parse_sample(image, num=parity)
    input_image = context["utils"].transforms.ToTensor()(input_image)
    input_image = input_image.unsqueeze(1)
    input_image = input_image.type(context["torch"].FloatTensor).to(context["device"])
    predicted_image = context["model"].test_on_batch(input_image)
    predicted_image = predicted_image.squeeze(1).squeeze(0)
    predicted_image = predicted_image.cpu().numpy()
    predicted_image = context["np"].around(predicted_image)
    if parity == 1:
        predicted_image = context["cv2"].rotate(predicted_image, rotateCode=context["cv2"].ROTATE_90_COUNTERCLOCKWISE)
    predicted_image_new = context["np"].zeros(image.shape)
    predicted_image_new[1:image.shape[0] - 1, 1:image.shape[1] - 1] = predicted_image
    return predicted_image_new


def matlab_expansion_extract_stage(image, predicted_image, parity, context):
    import matlab

    recovered, payload = context["engine"].cnn_expansion_extract(
        matlab.double(image.tolist()),
        matlab.double(predicted_image.tolist()),
        int(parity),
        nargout=2,
    )
    recovered_image = context["np"].array(recovered, dtype=context["np"].float64)
    payload_bits = [int(bit) for row in payload for bit in row]
    return recovered_image, payload_bits


def _count_sequence_errors(expected, actual):
    errors = sum(1 for left, right in zip(expected, actual) if left != right)
    return errors + abs(len(expected) - len(actual))


def _flatten(values):
    if hasattr(values, "flatten"):
        for value in values.flatten():
            yield int(value)
        return
    for value in values:
        if isinstance(value, (list, tuple)):
            yield from _flatten(value)
        else:
            yield int(value)
