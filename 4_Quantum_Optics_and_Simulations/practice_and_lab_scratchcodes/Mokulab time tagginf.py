import numpy as np
import matplotlib.pyplot as plt

# Define file names
file_path = "qrng1x_20250311_151526_Histograms.csv"
output_bin_file = "qrng_output.bin"  # Binary file
output_txt_file = "qrng_output.txt"  # Text file (human-readable)

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
bit_stream = (time_diffs * 1e12).astype(int) % 2  # Convert to picoseconds, take modulo 2

# Save binary output file
bit_bytes = np.packbits(bit_stream)  # Convert bit array to packed bytes
with open(output_bin_file, "wb") as f_bin:
    f_bin.write(bit_bytes)

# Save text file with raw binary data
with open(output_txt_file, "w") as f_txt:
    f_txt.write("".join(map(str, bit_stream)))  # Convert bit array to string and save

# Plot histogram of time differences
plt.figure(figsize=(8, 5))
plt.hist(time_diffs * 1e9, bins=50, color='blue', alpha=0.7, edgecolor='black')
plt.xlabel("Time Difference (ns)")
plt.ylabel("Counts")
plt.title("Time Difference Distribution (Photon Arrivals)")
plt.grid()
plt.show()

print(f"QRNG binary file saved as: {output_bin_file}")
print(f"QRNG text file saved as: {output_txt_file}")
print(f"Generated {len(bit_stream)} random bits.")
