import hashlib
import matplotlib.pyplot as plt
from scipy.stats import entropy as shannon_entropy
from math import floor

# -----------------------------
# Step 1: Parse Ch1 Timestamps Only (Event A = source 1)
# -----------------------------
def parse_ch1_arrival_times(filename):
    ch1_timestamps = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            try:
                source, timestamp = line.split(',')
                if int(source.strip()) == 1:
                    ch1_timestamps.append(float(timestamp.strip()))
            except ValueError:
                continue

    ch1_timestamps.sort()
    return ch1_timestamps

# -----------------------------
# Step 2: Convert Time Differences to Raw Bitstream
# -----------------------------
def generate_raw_bits_from_arrivals(timestamps):
    inter_arrival_times = [t2 - t1 for t1, t2 in zip(timestamps, timestamps[1:])]
    median = sorted(inter_arrival_times)[len(inter_arrival_times) // 2]

    raw_bits = ''.join(['1' if delta > median else '0' for delta in inter_arrival_times])
    return raw_bits

# -----------------------------
# Von Neumann Extractor
# -----------------------------
def von_neumann_extractor(raw_bits):
    output_bits = []
    i = 0
    while i < len(raw_bits) - 1:
        a, b = raw_bits[i], raw_bits[i + 1]
        if a != b:
            output_bits.append(b)
        i += 2
    return ''.join(output_bits)

# -----------------------------
# SHA-256 Extractor
# -----------------------------
def sha256_extractor(bitstring, chunk_size=512):
    output_bits = ""
    usable_length = floor(len(bitstring) / chunk_size) * chunk_size
    for i in range(0, usable_length, chunk_size):
        chunk = bitstring[i:i + chunk_size]
        byte_data = int(chunk, 2).to_bytes(chunk_size // 8, byteorder='big')
        hash_bits = bin(int(hashlib.sha256(byte_data).hexdigest(), 16))[2:].zfill(256)
        output_bits += hash_bits
    return output_bits

# -----------------------------
# Entropy Amplifier
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
    print(f"Saved {len(bitstring)} bits to '{filename}'.")

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
    print(f"Estimated Shannon Entropy: {h:.5f} bits/bit")
    return h

# -----------------------------
# MAIN QRNG PIPELINE (ToA-based)
# -----------------------------
def qrng_pipeline_toa(input_file):
    print("\nStep 1: Parsing Ch1 Arrival Times...")
    timestamps = parse_ch1_arrival_times(input_file)
    print(f"Total Ch1 timestamps: {len(timestamps)}")

    print("\nStep 2: Generating Raw Bits from Inter-Arrival Times...")
    raw_bits = generate_raw_bits_from_arrivals(timestamps)
    print(f"Raw bitstream length: {len(raw_bits)}")
    write_bits_to_file(raw_bits, "toa_raw_bits.txt")
    plot_bit_distribution(raw_bits, "Raw Bit Distribution (ToA)")
    estimate_entropy(raw_bits)

    print("\nStep 3: Von Neumann Debiasing...")
    debiased_bits = von_neumann_extractor(raw_bits)
    print(f"Debiased bitstream length: {len(debiased_bits)}")
    write_bits_to_file(debiased_bits, "toa_debiased_bits.txt")
    plot_bit_distribution(debiased_bits, "Debiased Bit Distribution")
    estimate_entropy(debiased_bits)

    if len(debiased_bits) < 512:
        print("Not enough bits for SHA-256 extraction. Exiting early.")
        return

    print("\nStep 4: SHA-256 Entropy Extraction...")
    sha256_bits = sha256_extractor(debiased_bits)
    print(f"SHA-256 extracted bitstream length: {len(sha256_bits)}")
    write_bits_to_file(sha256_bits, "toa_sha256_bits.txt")
    plot_bit_distribution(sha256_bits, "SHA-256 Extracted Bit Distribution")
    estimate_entropy(sha256_bits)

    print("\nStep 5: Entropy Amplification to ≥400,000 bits...")
    amplified_bits = entropy_amplifier_sha256(sha256_bits, target_length=400_000)
    write_bits_to_file(amplified_bits, "toa_amplified_400k.txt")
    plot_bit_distribution(amplified_bits, "Amplified Bit Distribution")
    estimate_entropy(amplified_bits)

    print("\nToA-based QRNG pipeline completed successfully!")

# -----------------------------
# Run the ToA QRNG Pipeline
# -----------------------------
qrng_pipeline_toa("test.csv")  # Change this to your file
