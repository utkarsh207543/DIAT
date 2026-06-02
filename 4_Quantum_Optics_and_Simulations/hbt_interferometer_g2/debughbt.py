import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# =========================
# SETTINGS
# =========================
filename = "cleaned_timestamps.csv"
bin_width = 1e-9
window = 100e-9
smooth_sigma = 2

# =========================
# FAST CSV LOADER
# =========================
print("Reading CSV (fast mode)...")

ch1 = []
ch2 = []

with open(filename, "r") as f:
    for line in f:

        if line.startswith("%"):
            continue

        parts = line.strip().split(",")

        if len(parts) != 2:
            continue

        try:
            ch = int(parts[0])
            t = float(parts[1])

            if ch == 1:
                ch1.append(t)

            elif ch == 2:
                ch2.append(t)

        except:
            continue


ch1 = np.array(ch1)
ch2 = np.array(ch2)

print("Loaded events:")
print("Ch1:", len(ch1))
print("Ch2:", len(ch2))


# =========================
# ACQUISITION TIME + RATES
# =========================
timestamps = np.concatenate((ch1, ch2))

T = timestamps.max() - timestamps.min()

R1 = len(ch1) / T
R2 = len(ch2) / T

print("Acquisition time:", T)
print("Rates:", R1, R2)


# =========================
# COMPUTE DELAYS (FAST)
# =========================
print("Computing coincidence delays...")

delays = []

j_start = 0

for t1 in ch1:

    while j_start < len(ch2) and ch2[j_start] < t1 - window:
        j_start += 1

    j = j_start

    while j < len(ch2) and ch2[j] <= t1 + window:
        delays.append(ch2[j] - t1)
        j += 1


delays = np.array(delays)

print("Coincidence candidates:", len(delays))


# =========================
# HISTOGRAM
# =========================
bins = np.arange(-window, window + bin_width, bin_width)

hist, edges = np.histogram(delays, bins=bins)

tau = (edges[:-1] + edges[1:]) / 2


# =========================
# NORMALIZATION
# =========================
g2 = hist / (R1 * R2 * bin_width * T)


# =========================
# SMOOTHING
# =========================
if smooth_sigma > 0:
    g2 = gaussian_filter1d(g2, smooth_sigma)


# =========================
# AUTO DIP DETECTION
# =========================
dip_index = np.argmin(g2)

dip_window = 5

start = max(0, dip_index - dip_window)
end = min(len(g2), dip_index + dip_window)

dip_tau = np.mean(tau[start:end])

print("Detected dip offset:", dip_tau * 1e9, "ns")


# =========================
# SHIFT TIME AXIS
# =========================
tau_corrected = tau - dip_tau


# =========================
# FIND g2(0)
# =========================
zero_index = np.argmin(np.abs(tau_corrected))

print("g²(0) =", g2[zero_index])


# =========================
# PLOT RESULT
# =========================
plt.figure(figsize=(8,4))

plt.bar(tau_corrected * 1e9, g2, width=bin_width * 1e9)

plt.axvline(0, linestyle="--")

plt.xlabel("Delay τ (ns)")
plt.ylabel("g²(τ)")
plt.title("Aligned g²(τ)")

plt.grid(True)

plt.show()