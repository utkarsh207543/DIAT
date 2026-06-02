# Realtime QRNG Python Receiver & Post-Processing
import serial
import hashlib
import matplotlib.pyplot as plt
from scipy.stats import entropy
from math import floor
import os

# Initialize plot
fig, ax = plt.subplots()
bars = ax.bar(['0', '1'], [0, 0])
plt.title("Live QRNG Bit Distribution")
plt.ylabel("Count")
plt.ion()
plt.show()

OUTPUT_FILE = "qrng_output_live.txt"

def append_to_file(bitstring):
    with open(OUTPUT_FILE, 'a') as f:
        f.write(bitstring)

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

def estimate_entropy(bitstring):
    p0 = bitstring.count('0') / len(bitstring)
    p1 = bitstring.count('1') / len(bitstring)
    h = entropy([p0, p1], base=2) if 0 < p0 < 1 else 0
    print(f"\u2139\ufe0f  Estimated Shannon Entropy: {h:.5f} bits/bit")
    return h

def update_plot(bitstring):
    zeros = bitstring.count('0')
    ones = bitstring.count('1')
    bars[0].set_height(zeros)
    bars[1].set_height(ones)
    plt.draw()
    plt.pause(0.001)

# Live read from serial
ser = serial.Serial('COM6', 115200, timeout=1)  # Change 'COM7' as needed
raw_bits = ""

try:
    print("\n📡 Listening to QRNG serial output... Press Ctrl+C to stop\n")
    while True:
        byte_str = ser.read().decode(errors='ignore')
        if byte_str.isdigit():  # Check if numeric character
            num = int(byte_str)
            bin_str = format(num, '04b')  # Convert to 4-bit binary
            raw_bits += bin_str
            append_to_file(bin_str)
            print(f"[+] Received: {byte_str} -> {bin_str}")

            if len(raw_bits) >= 2048:
                print("\n🧹 Von Neumann Debiasing...")
                debiased = von_neumann_extractor(raw_bits)
                print(f"Debiased length: {len(debiased)}")

                print("🔐 SHA-256 Extraction...")
                hashed = sha256_extractor(debiased)
                print(f"Hashed length: {len(hashed)}")

                update_plot(hashed)
                estimate_entropy(hashed)

                raw_bits = ""  # Reset buffer
except KeyboardInterrupt:
    print("\n🛑 Stopped QRNG live stream.")
    ser.close()
