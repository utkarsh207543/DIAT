import numpy as np
import matplotlib.pyplot as plt

# =========================
# SETTINGS
# =========================
filename = "x5.csv"

# Sweep ranges
bin_width_list = np.linspace(1e-9, 30e-9, 20)
window_list = np.linspace(50e-9, 800e-9, 20)

# =========================
# LOAD CSV
# =========================
data = np.genfromtxt(filename, delimiter=',', comments='%')
data = data[~np.isnan(data).any(axis=1)]

channel = data[:, 0].astype(int)
timestamps = data[:, 1]

# Sort timestamps
sort_idx = np.argsort(timestamps)
timestamps = timestamps[sort_idx]
channel = channel[sort_idx]

ch1 = timestamps[channel == 1]
ch2 = timestamps[channel == 2]

print("Counts:")
print("N1 =", len(ch1))
print("N2 =", len(ch2))

T = timestamps.max() - timestamps.min()

# =========================
# FUNCTION TO COMPUTE g2(0)
# =========================
def compute_g2(bin_width, window):

    delays = []
    j = 0

    for t1 in ch1:

        while j < len(ch2) and ch2[j] < t1 - window:
            j += 1

        k = j

        while k < len(ch2) and ch2[k] <= t1 + window:
            delays.append(ch2[k] - t1)
            k += 1

    if len(delays) == 0:
        return np.nan

    delays = np.array(delays)

    bins = np.arange(-window, window + bin_width, bin_width)

    hist, edges = np.histogram(delays, bins=bins)

    tau = (edges[:-1] + edges[1:]) / 2

    R1 = len(ch1) / T
    R2 = len(ch2) / T

    g2_tau = hist / (R1 * R2 * bin_width * T)

    center_bin = np.argmin(np.abs(tau))

    return g2_tau[center_bin]


# =========================
# SWEEP PARAMETERS
# =========================
results = np.zeros((len(window_list), len(bin_width_list)))

for i, window in enumerate(window_list):
    for j, bin_width in enumerate(bin_width_list):

        results[i, j] = compute_g2(bin_width, window)

# =========================
# FIND BEST VALUE
# =========================
best_idx = np.nanargmin(results)

best_window = window_list[best_idx // len(bin_width_list)]
best_bin = bin_width_list[best_idx % len(bin_width_list)]

best_g2 = np.nanmin(results)

print("\nBest parameters found:")
print("Best window =", best_window * 1e9, "ns")
print("Best bin width =", best_bin * 1e9, "ns")
print("Minimum g2(0) =", best_g2)

# =========================
# HEATMAP PLOT
# =========================
plt.figure(figsize=(8,6))

plt.imshow(
    results,
    extent=[
        bin_width_list[0]*1e9,
        bin_width_list[-1]*1e9,
        window_list[0]*1e9,
        window_list[-1]*1e9
    ],
    aspect='auto',
    origin='lower'
)

plt.colorbar(label="g²(0)")

plt.xlabel("Bin width (ns)")
plt.ylabel("Window size (ns)")
plt.title("Optimization map for g²(0)")

plt.show()