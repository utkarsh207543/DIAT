import numpy as np
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm

# ----------------------------
# Parameters
# ----------------------------
filename = "test.csv"  # Replace with your file name
bin_width = 1e-8            # 10 ns
max_delay = 1e-6            # ±1 μs

# ----------------------------
# Read timestamps from CSV
# ----------------------------
def read_spad_timestamps(filename):
    timestamps = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if not row or row[0].startswith('%') or row[0].strip().lower() == 'source':
                continue
            try:
                timestamp = float(row[1])
                timestamps.append(timestamp)
            except (ValueError, IndexError):
                continue
    return np.array(sorted(timestamps))

timestamps = read_spad_timestamps(filename)
print(f"✅ Loaded {len(timestamps)} timestamps")

# ----------------------------
# Compute symmetric g²(τ)
# ----------------------------
def compute_symmetric_g2(timestamps, bin_width, max_delay):
    delays = []
    n = len(timestamps)
    for i in tqdm(range(n)):
        for j in range(i+1, n):
            dt = timestamps[j] - timestamps[i]
            if dt > max_delay:
                break
            delays.append(dt)
            delays.append(-dt)  # for symmetry
    delays = np.array(delays)

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, _ = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bin_centers, g2

bin_centers, g2_values = compute_symmetric_g2(timestamps, bin_width, max_delay)

# ----------------------------
# Plot g²(τ)
# ----------------------------
plt.figure(figsize=(6, 4))
plt.plot(bin_centers * 1e9, g2_values, color='black', linewidth=1.5)
plt.title(r"$g^{(2)}(\tau)$ for SPAD (Autocorrelation)", fontsize=14)
plt.xlabel(r"Time Delay $\tau$ (ns)", fontsize=12)
plt.ylabel(r"$g^{(2)}(\tau)$", fontsize=12)
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)
plt.tight_layout()
plt.show()

# ----------------------------
# Analyze g²(0)
# ----------------------------
# Find the bin closest to τ=0
g2_zero_index = np.argmin(np.abs(bin_centers))
g2_zero_value = g2_values[g2_zero_index]

print(f"\n📊 g²(0) = {g2_zero_value:.3f}")

# Interpretation
if g2_zero_value < 1:
    print("🟢 Antibunched light (quantum, single-photon source)")
elif np.isclose(g2_zero_value, 1, atol=0.05):
    print("🟡 Poissonian / Random (coherent laser)")
else:
    print("🔴 Bunched light (thermal or classical source)")
