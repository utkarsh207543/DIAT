import numpy as np
import matplotlib.pyplot as plt
import hashlib

# Define file names
file_path = "test.csv"
raw_output_bin = "qrng_output_raw.bin"  # Raw binary file
raw_output_txt = "qrng_output_raw.txt"  # Raw text file (human-readable)
post_output_bin = "qrng_output_post.bin"  # Processed binary file
post_output_txt = "qrng_output_post.txt"  # Processed text file

# Read the file, skipping lines that start with '%'
with open(file_path, "r") as file:
    lines = file.readlines()

# Filter out comment lines (starting with '%')
data_lines = [line for line in lines if not line.startswith("%")]

# Convert to NumPy array
data = np.loadtxt(data_lines, delimiter=",")

# Extract time column (in seconds)
time_s = data[:, 0]

# Compute time differences between consecutive clicks
time_diffs = np.diff(time_s)

# Normalize time differences using modulo 2 method
raw_bits = (time_diffs * 1e12).astype(int) % 2  # Convert to picoseconds, take modulo 2

# Save raw binary output file
bit_bytes = np.packbits(raw_bits)
with open(raw_output_bin, "wb") as f_bin:
    f_bin.write(bit_bytes)

# Save raw text file
with open(raw_output_txt, "w") as f_txt:
    f_txt.write("".join(map(str, raw_bits)))

# Plot histogram of time differences
plt.figure(figsize=(8, 5))
plt.hist(time_diffs * 1e9, bins=50, color='blue', alpha=0.7, edgecolor='black')
plt.xlabel("Time Difference (ns)")
plt.ylabel("Counts")
plt.title("Time Difference Distribution (Photon Arrivals)")
plt.grid()
plt.show()

print(f"Raw QRNG binary file saved as: {raw_output_bin}")
print(f"Raw QRNG text file saved as: {raw_output_txt}")
print(f"Generated {len(raw_bits)} raw random bits.")

### **Post-Processing for NIST Compliance** ###

# 1. **Von Neumann Debiasing**
debias_bits = []
for i in range(0, len(raw_bits) - 1, 2):
    if raw_bits[i] == 0 and raw_bits[i + 1] == 1:
        debias_bits.append(0)
    elif raw_bits[i] == 1 and raw_bits[i + 1] == 0:
        debias_bits.append(1)

debias_bits = np.array(debias_bits, dtype=np.uint8)
print(f"Von Neumann Output: {len(debias_bits)} bits")

# 2. **XOR Mixing with Shifted Data**
xor_bits = debias_bits[:-1] ^ debias_bits[1:]
print(f"XOR Mixed Output: {len(xor_bits)} bits")

# 3. **Hashing (SHA-256 Compression)**
hashed_bits = []
for i in range(0, len(xor_bits), 256):
    chunk = "".join(map(str, xor_bits[i:i+256]))
    if len(chunk) < 256:
        break
    hash_digest = hashlib.sha256(chunk.encode()).hexdigest()
    hashed_bits.extend(bin(int(hash_digest, 16))[2:].zfill(256))

hashed_bits = np.array(list(map(int, hashed_bits)), dtype=np.uint8)
print(f"SHA-256 Output: {len(hashed_bits)} bits")

# Save processed binary file
bit_bytes = np.packbits(hashed_bits)
with open(post_output_bin, "wb") as f_bin:
    f_bin.write(bit_bytes)

# Save processed text file with formatted columns
bits_per_row = 25  # Adjust column width as needed

with open(post_output_txt, "w") as f_txt:
    for i in range(0, len(hashed_bits), bits_per_row):
        f_txt.write("".join(map(str, hashed_bits[i:i+bits_per_row])) + "\n")

print(f"Processed QRNG binary file saved as: {post_output_bin}")
print(f"Processed QRNG text file saved as: {post_output_txt}")
print(f"Generated {len(hashed_bits)} final random bits in formatted columns.")
