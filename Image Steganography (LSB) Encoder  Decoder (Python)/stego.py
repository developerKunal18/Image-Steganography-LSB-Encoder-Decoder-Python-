

import sys
from PIL import Image
import hashlib

# ---------- Helpers ----------
def _text_to_bits(text: str) -> str:
    return "".join(f"{ord(c):08b}" for c in text)

def _bits_to_text(bits: str) -> str:
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return "".join(chr(int(c, 2)) for c in chars if len(c) == 8)

def _derive_key(password: str, length: int) -> bytes:
    # Expand sha256 digest to needed length via repeated hashing
    key = b""
    cur = password.encode("utf-8")
    while len(key) < length:
        cur = hashlib.sha256(cur).digest()
        key += cur
        cur = cur  # continue with digest
    return key[:length]

def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i,b in enumerate(data))

# ---------- Core LSB functions ----------
def encode_image(input_path: str, message: str, output_path: str, password: str = None):
    img = Image.open(input_path)
    if img.mode not in ("RGB","RGBA"):
        img = img.convert("RGBA")

    pixels = list(img.getdata())
    width, height = img.size
    total_pixels = width * height
    channels = 3  # we'll use RGB channels (ignore alpha for embedding)
    capacity_bits = total_pixels * channels

    # prepare message: length header (32 bits) + payload bits
    data_bytes = message.encode("utf-8")
    if password:
        key = _derive_key(password, len(data_bytes))
        data_bytes = _xor_bytes(data_bytes, key)

    payload_bits = "".join(f"{b:08b}" for b in data_bytes)
    msg_len = len(payload_bits)  # number of payload bits
    header = f"{msg_len:032b}"  # 32-bit unsigned length header
    full_bits = header + payload_bits

    if len(full_bits) > capacity_bits:
        raise ValueError(f"Message too large to fit in image. Capacity {capacity_bits} bits, need {len(full_bits)} bits.")

    # embed bits into LSBs of R,G,B channels sequentially
    new_pixels = []
    bit_iter = iter(full_bits)
    for px in pixels:
        r,g,b,a = (px[0], px[1], px[2], px[3]) if len(px) == 4 else (px[0], px[1], px[2], 255)
        new_rgb = []
        for channel in (r,g,b):
            try:
                bit = next(bit_iter)
                channel = (channel & ~1) | int(bit)
            except StopIteration:
                # no more bits: keep remaining channels unchanged
                pass
            new_rgb.append(channel)
        if len(px) == 4:
            new_pixels.append((new_rgb[0], new_rgb[1], new_rgb[2], a))
        else:
            new_pixels.append((new_rgb[0], new_rgb[1], new_rgb[2]))

    # create output image
    out_img = Image.new(img.mode, img.size)
    out_img.putdata(new_pixels)
    out_img.save(output_path, "PNG")
    print(f"✅ Encoded message into {output_path} (used {len(full_bits)} bits)")

def decode_image(stego_path: str, password: str = None) -> str:
    img = Image.open(stego_path)
    if img.mode not in ("RGB","RGBA"):
        img = img.convert("RGBA")
    pixels = list(img.getdata())

    # read first 32 bits to get payload length
    bits = []
    for px in pixels:
        r,g,b = px[0], px[1], px[2]
        bits.append(str(r & 1))
        if len(bits) >= 32:
            break
        bits.append(str(g & 1))
        if len(bits) >= 32:
            break
        bits.append(str(b & 1))
        if len(bits) >= 32:
            break
    header_bits = "".join(bits[:32])
    payload_len = int(header_bits, 2)

    # read payload_len bits
    bits = []
    bit_count = 0
    # start reading from beginning again but skip header bits while counting
    consumed = 0
    for px in pixels:
        for channel in (px[0], px[1], px[2]):
            if consumed < 32:
                consumed += 1
                continue
            if bit_count < payload_len:
                bits.append(str(channel & 1))
                bit_count += 1
            else:
                break
        if bit_count >= payload_len:
            break

    payload_bits = "".join(bits)
    # pad to multiple of 8
    if len(payload_bits) % 8 != 0:
        # discard trailing bits to make full bytes
        payload_bits = payload_bits[:(len(payload_bits)//8)*8]

    data = bytes(int(payload_bits[i:i+8], 2) for i in range(0, len(payload_bits), 8))
    if password:
        key = _derive_key(password, len(data))
        data = _xor_bytes(data, key)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="replace")
    return text

# ---------- CLI ----------
def _usage():
    print("Usage:")
    print("  Encode: python stego.py encode input.png \"secret message\" output.png [password]")
    print("  Decode: python stego.py decode stego.png [password]")

def main():
    if len(sys.argv) < 3:
        _usage()
        return
    mode = sys.argv[1].lower()
    if mode == "encode":
        if len(sys.argv) < 5:
            _usage(); return
        inp = sys.argv[2]
        msg = sys.argv[3]
        out = sys.argv[4]
        pwd = sys.argv[5] if len(sys.argv) >=6 else None
        try:
            encode_image(inp, msg, out, password=pwd)
        except Exception as e:
            print("Error:", e)
    elif mode == "decode":
        inp = sys.argv[2]
        pwd = sys.argv[3] if len(sys.argv) >=4 else None
        try:
            text = decode_image(inp, password=pwd)
            print("🔓 Hidden message:")
            print(text)
        except Exception as e:
            print("Error:", e)
    else:
        _usage()

if __name__ == "__main__":
    main()
