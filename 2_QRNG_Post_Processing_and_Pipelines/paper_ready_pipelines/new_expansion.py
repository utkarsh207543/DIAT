import hashlib

# ==============================
# PARAMETERS
# ==============================
INPUT_FILE = "Utkarsh_QRNG_10.txt"
OUTPUT_FILE = "output2.txt"

TARGET_BITS = 2_000_000

# ==============================
# PARSE TIME-TAGGED DATA
# ==============================
def parse_qrng_file(filename):
    events = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue

            parts = line.split()
            try:
                if parts[0].isdigit():
                    events.append((int(parts[0]), '0'))
                if len(parts) > 1 and parts[1].isdigit():
                    events.append((int(parts[1]), '1'))
            except ValueError:
                continue

    events.sort(key=lambda x: x[0])
    return ''.join(bit for _, bit in events)

# ==============================
# VON NEUMANN DEBIASING
# ==============================
def von_neumann(bits):
    out = []
    for i in range(0, len(bits) - 1, 2):
        a, b = bits[i], bits[i + 1]
        if a != b:
            out.append(b)
    return ''.join(out)

# ==============================
# SHA-256 COUNTER-MODE EXPANSION
# ==============================
def sha256_expand(seed_bits, target_bits):
    out_bits = ""
    counter = 0

    while len(out_bits) < target_bits:
        counter_bits = format(counter, '032b')
        data = seed_bits + counter_bits

        data_bytes = int(data, 2).to_bytes((len(data) + 7) // 8, 'big')
        digest = hashlib.sha256(data_bytes).digest()

        out_bits += ''.join(f"{b:08b}" for b in digest)
        counter += 1

    return out_bits[:target_bits]

# ==============================
# MAIN PIPELINE
# ==============================
def qrng_pipeline():
    print("🔹 Parsing raw QRNG data...")
    raw_bits = parse_qrng_file(INPUT_FILE)
    print(f"Raw bits: {len(raw_bits):,}")

    print("🔹 Von Neumann debiasing...")
    vn_bits = von_neumann(raw_bits)
    print(f"After VN: {len(vn_bits):,}")

    if len(vn_bits) < 10_000:
        raise RuntimeError("❌ VN output too small to act as entropy seed")

    print("🔹 SHA-256 entropy expansion...")
    final_bits = sha256_expand(vn_bits, TARGET_BITS)

    print(f"Final output bits: {len(final_bits):,}")

    with open(OUTPUT_FILE, "w") as f:
        f.write(final_bits)

    print(f"\n✅ SUCCESS: {TARGET_BITS:,} bits written to '{OUTPUT_FILE}'")

# ==============================
if __name__ == "__main__":
    qrng_pipeline()
