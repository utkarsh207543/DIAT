import hashlib
import matplotlib.pyplot as plt
from scipy.stats import entropy
from math import floor

def read_bitstring_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    bitstring = ''.join(line.strip() for line in lines if set(line.strip()).issubset({'0', '1'}))
    return bitstring

def von_neumann_extractor(raw_bits):
    output_bits = []
    i = 0
    while i < len(raw_bits) - 1:
        a, b = raw_bits[i], raw_bits[i+1]
        if a != b:
            output_bits.append(b)
        i += 2
    return ''.join(output_bits)

def sha256_extractor(bitstring, chunk_size=512):
    output_bits = ""
    usable_length = floor(len(bitstring) / chunk_size) * chunk_size
    for i in range(0, usable_length, chunk_size):
        chunk = bitstring[i:i+chunk_size]
        byte_data = int(chunk, 2).to_bytes(chunk_size // 8, byteorder='big')
        hash_bits = bin(int(hashlib.sha256(byte_data).hexdigest(), 16))[2:].zfill(256)
        output_bits += hash_bits
    return output_bits

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
    h = entropy([p0, p1], base=2) if 0 < p0 < 1 else 0
    print(f"ℹ️  Estimated Shannon Entropy: {h:.5f} bits/bit")
    return h

def qrng_pipeline_from_bits_file(input_file):
    print("\n🔍 Step 1: Reading Bitstring File...")
    raw_bits = read_bitstring_file(input_file)
    print(f"Raw bitstream length: {len(raw_bits)}")

    plot_bit_distribution(raw_bits, "Raw Bit Distribution")
    estimate_entropy(raw_bits)
    write_bits_to_file(raw_bits, "qrng_raw_bits.txt")

    print("\n🧹 Step 2: Von Neumann Debiasing...")
    debiased_bits = von_neumann_extractor(raw_bits)
    print(f"Debiased bitstream length: {len(debiased_bits)}")

    plot_bit_distribution(debiased_bits, "Debiased Bit Distribution")
    estimate_entropy(debiased_bits)
    write_bits_to_file(debiased_bits, "qrng_debiased_bits.txt")

    print("\n🔐 Step 3: SHA-256 Entropy Extraction...")
    sha256_bits = sha256_extractor(debiased_bits)
    print(f"SHA-256 extracted bitstream length: {len(sha256_bits)}")

    plot_bit_distribution(sha256_bits, "SHA-256 Extracted Bit Distribution")
    estimate_entropy(sha256_bits)
    write_bits_to_file(sha256_bits, "qrng_sha256_extracted_bits.txt")

    print("\n✅ QRNG pipeline completed successfully.")

# Example usage
qrng_pipeline_from_bits_file("capture.txt")
