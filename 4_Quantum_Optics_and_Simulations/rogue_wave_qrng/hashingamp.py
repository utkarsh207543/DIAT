import hashlib

# =========================================
# PARAMETERS
# =========================================
EXPANDED_BITS = 8192   # how many final bits you want
BLOCK_SIZE = 256       # SHA-256 output size (bits)

# =========================================
# 1. READ RAW BITSTREAM
# =========================================
with open("output.txt", "r") as f:
    raw_bits = "".join(c for c in f.read() if c in "01")

print(f"[✓] Raw bits loaded: {len(raw_bits)}")

# =========================================
# 2. VON NEUMANN EXTRACTOR
# =========================================
def von_neumann(bits):
    out = []
    for i in range(0, len(bits) - 1, 2):
        pair = bits[i:i+2]
        if pair == "01":
            out.append("0")
        elif pair == "10":
            out.append("1")
    return "".join(out)

vn_bits = von_neumann(raw_bits)
print(f"[✓] After Von Neumann: {len(vn_bits)} bits")

if len(vn_bits) < 512:
    raise ValueError("Not enough entropy after Von Neumann extraction")

# =========================================
# 3. ENTROPY EXTRACTION (SHA-256)
# =========================================
def sha256_extract(bitstring):
    byte_array = bytearray(
        int(bitstring[i:i+8], 2)
        for i in range(0, len(bitstring) - 7, 8)
    )
    digest = hashlib.sha256(byte_array).digest()
    return digest

seed = sha256_extract(vn_bits)
print("[✓] SHA-256 entropy extraction complete (256-bit seed)")

# =========================================
# 4. ENTROPY EXPANSION (COUNTER-MODE PRG)
# =========================================
def expand_entropy(seed, n_bits):
    output_bits = ""
    counter = 0

    while len(output_bits) < n_bits:
        counter_bytes = counter.to_bytes(4, "big")
        digest = hashlib.sha256(seed + counter_bytes).digest()
        output_bits += "".join(f"{b:08b}" for b in digest)
        counter += 1

    return output_bits[:n_bits]

expanded_bits = expand_entropy(seed, EXPANDED_BITS)

print(f"[✓] Entropy expanded to {len(expanded_bits)} bits")

# =========================================
# 5. SAVE FINAL OUTPUT
# =========================================
with open("final_random_bits.txt", "w") as f:
    f.write(expanded_bits)

print("[✓] Saved final_random_bits.txt")
