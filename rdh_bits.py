def normalize_bits(bits):
    normalized = []
    for bit in bits:
        value = int(bit)
        if value not in (0, 1):
            raise ValueError(f"bit must be 0 or 1, got {bit!r}")
        normalized.append(value)
    return normalized


def ensure_even_bit_count(bits):
    normalized = normalize_bits(bits)
    if len(normalized) % 2 != 0:
        raise ValueError("扩展嵌入当前两阶段实现要求秘密信息比特数为偶数")
    return normalized


def text_to_bits(text, encoding="utf-8"):
    data = text.encode(encoding)
    return [(byte >> shift) & 1 for byte in data for shift in range(7, -1, -1)]


def bits_to_bytes(bits):
    normalized = normalize_bits(bits)
    if len(normalized) % 8 != 0:
        raise ValueError("提取出的比特数不是 8 的倍数，无法按 UTF-8 文本解码")
    output = bytearray()
    for index in range(0, len(normalized), 8):
        value = 0
        for bit in normalized[index:index + 8]:
            value = (value << 1) | bit
        output.append(value)
    return bytes(output)


def bits_to_text(bits, encoding="utf-8"):
    return bits_to_bytes(bits).decode(encoding)
