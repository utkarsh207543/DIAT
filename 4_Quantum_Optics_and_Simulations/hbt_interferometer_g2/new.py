import numpy as np
import matplotlib.pyplot as plt

# =========================
# SETTINGS
# =========================
filename = "ultra_cleaned_timestamps.csv"

bin_width = 1e-9
window = 50e-9

# =========================
# LOAD CSV (ROBUST LOADER)
# =========================
data = np.genfromtxt(
    filename,
    delimiter=',',
    comments='%'
)

# Remove empty / corrupted rows
data = data[~np.isnan(data).any(axis=1)]

channel = data[:, 0].astype(int)
timestamps = data[:, 1]

# Ensure timestamps sorted
sort_idx = np.argsort(timestamps)
timestamps = timestamps[sort_idx]
channel = channel[sort_idx]

# Split channels
ch1 = timestamps[channel == 1]
ch2 = timestamps[channel == 2]

print("Counts:")
print("N1 =", len(ch1))
print("N2 =", len(ch2))

# =========================
# BUILD DELAY HISTOGRAM
# =========================
delays = []

j = 0

for t1 in ch1:

    while j < len(ch2) and ch2[j] < t1 - window:
        j += 1

    k = j

    while k < len(ch2) and ch2[k] <= t1 + window:
        delays.append(ch2[k] - t1)
        k += 1

delays = np.array(delays)

# =========================
# HISTOGRAM
# =========================
bins = np.arange(-window, window + bin_width, bin_width)

hist, edges = np.histogram(delays, bins=bins)

tau = (edges[:-1] + edges[1:]) / 2

# =========================
# NORMALIZATION → g2(tau)
# =========================
T = timestamps.max() - timestamps.min()

R1 = len(ch1) / T
R2 = len(ch2) / T

g2_tau = hist / (R1 * R2 * bin_width * T)

# =========================
# PLOT
# =========================
plt.figure(figsize=(8,5))
plt.plot(tau * 1e9, g2_tau, marker='o')

plt.xlabel("Delay τ (ns)")
plt.ylabel("g²(τ)")
plt.title("Second-order correlation function g²(τ)")
plt.grid(True)

plt.tight_layout()
plt.show()

# =========================
# PRINT g2(0)
# =========================
center_bin = np.argmin(np.abs(tau))
print("\ng2(0) ≈", g2_tau[center_bin])