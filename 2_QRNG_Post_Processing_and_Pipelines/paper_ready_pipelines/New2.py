import hashlib

# ==============================
# PARAMETERS
# ==============================
INPUT_FILE = "Utkarsh_QRNG_10.txt"
OUTPUT_FILE = "output_new2.txt"

TARGET_BITS = 2_000_000

# Choose expansion model:
# "refresh"  -> SHA-256 + entropy refresh (BEST for Universal)
# "xor"      -> SHA-256 keystream XOR VN bits
# "sliding"  -> Sliding-window SHA-256
EXPANSION_MODEL = "refresh"

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
# MODEL 1: SHA-256 + ENTROPY REFRESH
# ==============================
def sha256_expand_with_refresh(seed_bits, raw_bits, target_bits, refresh_bits=256):
    out = ""
    counter = 0
    raw_len = len(raw_bits)

    while len(out) < target_bits:
        start = (counter * refresh_bits) % (raw_len - refresh_bits)
        refresh = raw_bits[start:start + refresh_bits]

        data = seed_bits + refresh + format(counter, '032b')
        data_bytes = int(data, 2).to_bytes((len(data) + 7) // 8, 'big')

        digest = hashlib.sha256(data_bytes).digest()
        out += ''.join(f"{b:08b}" for b in digest)

        counter += 1

    return out[:target_bits]

# ==============================
# MODEL 2: SHA-256 KEYSTREAM XOR
# ==============================
def xor_stream_expand(seed_bits, vn_bits, target_bits):
    out = ""
    counter = 0
    vn_len = len(vn_bits)

    while len(out) < target_bits:
        data = seed_bits + format(counter, '032b')
        data_bytes = int(data, 2).to_bytes((len(data) + 7) // 8, 'big')

        digest = hashlib.sha256(data_bytes).digest()
        keystream = ''.join(f"{b:08b}" for b in digest)

        for i in range(len(keystream)):
            bit = str(int(keystream[i]) ^ int(vn_bits[(counter * 256 + i) % vn_len]))
            out += bit
            if len(out) >= target_bits:
                break

        counter += 1

    return out

# ==============================
# MODEL 3: SLIDING-WINDOW HASH
# ==============================
def sliding_sha256(bits, target_bits, window=1024, step=128):
    out = ""
    i = 0

    while len(out) < target_bits and i + window <= len(bits):
        chunk = bits[i:i + window]
        data_bytes = int(chunk, 2).to_bytes(window // 8, 'big')

        digest = hashlib.sha256(data_bytes).digest()
        out += ''.join(f"{b:08b}" for b in digest)

        i += step

    if len(out) < target_bits:
        raise RuntimeError("❌ Sliding window exhausted entropy")

    return out[:target_bits]

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

    print(f"🔹 Expansion model: {EXPANSION_MODEL}")

    if EXPANSION_MODEL == "refresh":
        final_bits = sha256_expand_with_refresh(
            seed_bits=vn_bits,
            raw_bits=raw_bits,
            target_bits=TARGET_BITS
        )

    elif EXPANSION_MODEL == "xor":
        final_bits = xor_stream_expand(
            seed_bits=vn_bits,
            vn_bits=vn_bits,
            target_bits=TARGET_BITS
        )

    elif EXPANSION_MODEL == "sliding":
        final_bits = sliding_sha256(
            bits=vn_bits,
            target_bits=TARGET_BITS
        )

    else:
        raise ValueError("❌ Unknown expansion model selected")

    print(f"Final output bits: {len(final_bits):,}")

    with open(OUTPUT_FILE, "w") as f:
        f.write(final_bits)

    print(f"\n✅ SUCCESS: {TARGET_BITS:,} bits written to '{OUTPUT_FILE}'")

# ==============================
if __name__ == "__main__":
    qrng_pipeline()
