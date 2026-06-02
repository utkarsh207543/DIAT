import hashlib
import matplotlib.pyplot as plt
from scipy.stats import entropy as shannon_entropy
from math import floor

# -----------------------------
# Step 1: Parse QRNG Time-Tagged Data
# -----------------------------
def parse_qrng_file(filename):
    ch1_times = []
    ch2_times = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue

            values = line.split()
            while len(values) < 3:
                values.append(None)

            try:
                ch1 = int(values[0]) if values[0] is not None else None
                ch2 = int(values[1]) if values[1] is not None else None
            except ValueError:
                continue

            if ch1 is not None:
                ch1_times.append((ch1, '0'))
            if ch2 is not None:
                ch2_times.append((ch2, '1'))

    all_events = sorted(ch1_times + ch2_times, key=lambda x: x[0])
    return ''.join(bit for _, bit in all_events)

# -----------------------------
# Step 2: Von Neumann Extractor
# -----------------------------
def von_neumann_extractor(raw_bits):
    output_bits = []
    i = 0
    while i < len(raw_bits) - 1:
        a, b = raw_bits[i], raw_bits[i+1]
        if a != b:
            output_bits.append(b)
        i += 2
    return ''.join(output_bits)

# -----------------------------
# Step 3: SHA-256 Block Extractor
# -----------------------------
def sha256_extractor(bitstring, chunk_size=512):
    output_bits = ""
    usable_length = floor(len(bitstring) / chunk_size) * chunk_size
    for i in range(0, usable_length, chunk_size):
        chunk = bitstring[i:i+chunk_size]
        byte_data = int(chunk, 2).to_bytes(chunk_size // 8, byteorder='big')
        hash_bits = bin(int(hashlib.sha256(byte_data).hexdigest(), 16))[2:].zfill(256)
        output_bits += hash_bits
    return output_bits

# -----------------------------
# Step 4: Entropy Amplifier using SHA-256 + Counter
# -----------------------------
def entropy_amplifier_sha256(seed_bits, target_length=400_000):
    if len(seed_bits) < 256:
        raise ValueError("Need at least 256 seed bits to initialize amplification.")

    seed_bytes = int(seed_bits[:256], 2).to_bytes(32, byteorder='big')
    output_bits = ""
    counter = 0

    while len(output_bits) < target_length:
        counter_bytes = counter.to_bytes(8, byteorder='big')
        hash_input = seed_bytes + counter_bytes
        hash_digest = hashlib.sha256(hash_input).digest()
        hash_bits = bin(int.from_bytes(hash_digest, byteorder='big'))[2:].zfill(256)
        output_bits += hash_bits
        counter += 1

    return output_bits[:target_length]

# -----------------------------
# Helpers: Save, Plot, Entropy
# -----------------------------
def write_bits_to_file(bitstring, filename):
    with open(filename, 'w') as f:
        f.write(bitstring)
    print(f"✅ Saved {len(bitstring)} bits to '{filename}'.")

def plot_bit_distribution(bitstring, title="Bit Distribution"):
    zeros = bitstring.count('0')
    ones = bitstring.count('1')
    plt.bar(['0', '1'], [zeros, ones])
    plt.title(title)
    plt.ylabel('Count')
    plt.show()

def estimate_entropy(bitstring):
    p0 = bitstring.count('0') / len(bitstring)
    p1 = bitstring.count('1') / len(bitstring)
    h = shannon_entropy([p0, p1], base=2) if 0 < p0 < 1 else 0
    print(f"ℹ️  Estimated Shannon Entropy: {h:.5f} bits/bit")
    return h

# -----------------------------
# MAIN QRNG PIPELINE
# -----------------------------
def qrng_pipeline(input_file):
    print("\n🔍 Step 1: Parsing Time-Tagged Data...")
    raw_bits = parse_qrng_file(input_file)
    print(f"Raw bitstream length: {len(raw_bits)}")
    write_bits_to_file(raw_bits, "qrng_raw_bits.txt")
    plot_bit_distribution(raw_bits, "Raw Bit Distribution")
    estimate_entropy(raw_bits)

    print("\n🧹 Step 2: Von Neumann Debiasing...")
    debiased_bits = von_neumann_extractor(raw_bits)
    print(f"Debiased bitstream length: {len(debiased_bits)}")
    write_bits_to_file(debiased_bits, "qrng_debiased_bits.txt")
    plot_bit_distribution(debiased_bits, "Debiased Bit Distribution")
    estimate_entropy(debiased_bits)

    print("\n🔐 Step 3: SHA-256 Entropy Extraction...")
    sha256_bits = sha256_extractor(debiased_bits)
    print(f"SHA-256 extracted bitstream length: {len(sha256_bits)}")
    write_bits_to_file(sha256_bits, "qrng_sha256_extracted_bits.txt")
    plot_bit_distribution(sha256_bits, "SHA-256 Extracted Bit Distribution")
    estimate_entropy(sha256_bits)

    print("\n🚀 Step 4: Entropy Amplification to ≥400,000 bits...")
    amplified_bits = entropy_amplifier_sha256(sha256_bits, target_length=400_000)
    write_bits_to_file(amplified_bits, "qrng_sha256_amplified_400k.txt")
    plot_bit_distribution(amplified_bits, "Amplified Bit Distribution")
    estimate_entropy(amplified_bits)

    print("\n✅ QRNG pipeline completed successfully!")

# Run the full pipeline
qrng_pipeline("Utkarsh_QRNG_10.txt")
