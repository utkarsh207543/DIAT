import hashlib

# ===============================
# 1. READ RAW BITSTREAM
# ===============================
with open("output.txt", "r") as f:
    raw_bits = f.read().strip()

print(f"Raw bits loaded: {len(raw_bits)}")

# Remove any accidental characters
raw_bits = "".join(b for b in raw_bits if b in "01")

# ===============================
# 2. VON NEUMANN EXTRACTOR
# ===============================
def von_neumann(bits):
    out = []
    for i in range(0, len(bits) - 1, 2):
        pair = bits[i:i+2]
        if pair == "01":
            out.append("0")
        elif pair == "10":
            out.append("1")
        # 00 and 11 are discarded
    return "".join(out)

vn_bits = von_neumann(raw_bits)

print(f"After Von Neumann: {len(vn_bits)} bits")

if len(vn_bits) < 256:
    raise ValueError("Not enough entropy after Von Neumann extraction")

# ===============================
# 3. SHA-256 COMPRESSION
# ===============================
def sha256_bits(bitstring):
    # Convert bitstring → bytes
    byte_array = bytearray()
    for i in range(0, len(bitstring), 8):
        byte = bitstring[i:i+8]
        if len(byte) == 8:
            byte_array.append(int(byte, 2))

    digest = hashlib.sha256(byte_array).digest()

    # Convert hash → bitstring
    return "".join(f"{byte:08b}" for byte in digest)

final_bits = sha256_bits(vn_bits)

print(f"Final SHA-256 output: {len(final_bits)} bits")

# ===============================
# 4. SAVE FINAL OUTPUT
# ===============================
with open("output_vn_sha256.txt", "w") as f:
    f.write(final_bits)

print("✔ Saved output_vn_sha256.txt")
