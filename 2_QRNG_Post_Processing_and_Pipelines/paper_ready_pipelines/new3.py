import hashlib

# ==============================
# PARAMETERS
# ==============================
INPUT_FILE = "Utkarsh_QRNG_10.txt"
OUTPUT_FILE = "output_new3.txt"

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
# STRONG EXPANSION + POST-PROCESS
# ==============================
def strong_entropy_expand(vn_bits, raw_bits, target_bits):
    out = ""
    counter = 0

    raw_len = len(raw_bits)
    vn_len = len(vn_bits)

    if raw_len < 1024 or vn_len < 1024:
        raise RuntimeError("❌ Not enough entropy for strong expansion")

    while len(out) < target_bits:
        # --- Irregular refresh index (hash-driven) ---
        idx_seed = vn_bits[counter % vn_len : (counter % vn_len) + 256]
        idx_hash = hashlib.sha256(int(idx_seed, 2).to_bytes(32, 'big')).digest()
        idx = int.from_bytes(idx_hash[:4], 'big') % (raw_len - 512)

        refresh = raw_bits[idx : idx + 512]

        # --- First hash ---
        h1_input = vn_bits + refresh + format(counter, '032b')
        h1_bytes = int(h1_input, 2).to_bytes((len(h1_input) + 7) // 8, 'big')
        h1 = hashlib.sha256(h1_bytes).digest()

        h1_bits = ''.join(f"{b:08b}" for b in h1)

        # --- XOR with sliding VN bits ---
        mixed = []
        for i in range(len(h1_bits)):
            mixed.append(str(int(h1_bits[i]) ^ int(vn_bits[(counter*128 + i) % vn_len])))
        mixed_bits = ''.join(mixed)

        # --- Second hash (destroys structure) ---
        h2_bytes = int(mixed_bits, 2).to_bytes(len(mixed_bits) // 8, 'big')
        h2 = hashlib.sha256(h2_bytes).digest()

        out += ''.join(f"{b:08b}" for b in h2)

        counter += 1

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

    if len(vn_bits) < 20_000:
        raise RuntimeError("❌ VN output too small")

    print("🔹 Strong entropy expansion + post-processing...")
    final_bits = strong_entropy_expand(
        vn_bits=vn_bits,
        raw_bits=raw_bits,
        target_bits=TARGET_BITS
    )

    print(f"Final output bits: {len(final_bits):,}")

    with open(OUTPUT_FILE, "w") as f:
        f.write(final_bits)

    print(f"\n✅ SUCCESS: {TARGET_BITS:,} bits written to '{OUTPUT_FILE}'")

# ==============================
if __name__ == "__main__":
    qrng_pipeline()
