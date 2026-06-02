import numpy as np
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm

# ----------------------------
# Parameters
# ----------------------------
filename = "test5_bs.csv"  # Replace with your actual file
bin_width = 1e-8       # 10 ns
max_delay = 1e-6       # ±1 µs

# ----------------------------
# Read Ch1 and Ch2 from CSV
# ----------------------------
def read_channel_timestamps(filename):
    ch1 = []
    ch2 = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            try:
                source, timestamp = line.split(',')
                timestamp = float(timestamp.strip())
                if int(source.strip()) == 1:
                    ch1.append(timestamp)
                elif int(source.strip()) == 2:
                    ch2.append(timestamp)
            except ValueError:
                continue
    return np.array(sorted(ch1)), np.array(sorted(ch2))

ch1_timestamps, ch2_timestamps = read_channel_timestamps(filename)
print(f"✅ Ch1 loaded: {len(ch1_timestamps)} timestamps")
print(f"✅ Ch2 loaded: {len(ch2_timestamps)} timestamps")

# ----------------------------
# g²(τ) computation (autocorrelation)
# ----------------------------
def compute_symmetric_g2(timestamps, bin_width, max_delay):
    delays = []
    n = len(timestamps)
    for i in tqdm(range(n), desc="Computing g²"):
        for j in range(i+1, n):
            dt = timestamps[j] - timestamps[i]
            if dt > max_delay:
                break
            delays.append(dt)
            delays.append(-dt)
    delays = np.array(delays)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, _ = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) != 0 else hist
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bin_centers, g2

# ----------------------------
# HBT cross-correlation computation
# ----------------------------
def compute_hbt_cross_correlation(ch1, ch2, bin_width, max_delay):
    delays = []
    i = 0
    j = 0
    ch1 = np.sort(ch1)
    ch2 = np.sort(ch2)
    while i < len(ch1) and j < len(ch2):
        dt = ch2[j] - ch1[i]
        if abs(dt) <= max_delay:
            delays.append(dt)
            j += 1
        elif dt > max_delay:
            i += 1
        else:
            j += 1
    delays = np.array(delays)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, _ = np.histogram(delays, bins=bins)
    norm_hist = hist / np.mean(hist) if np.mean(hist) != 0 else hist
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bin_centers, norm_hist

# ----------------------------
# Fast g²(Δt) via FFT
# ----------------------------
def compute_g2_of_deltas_fast(delta_ts, bin_width, max_delay):
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    counts, _ = np.histogram(delta_ts, bins=bins)
    autocorr = np.correlate(counts, counts, mode='full')
    center = len(autocorr) // 2
    delays = np.arange(-len(counts) + 1, len(counts)) * bin_width
    g2 = autocorr / np.mean(autocorr)
    mask = np.abs(delays) <= max_delay
    return delays[mask], g2[mask]

# ----------------------------
# Compute All
# ----------------------------
bin_centers_ch1, g2_ch1 = compute_symmetric_g2(ch1_timestamps, bin_width, max_delay)
bin_centers_ch2, g2_ch2 = compute_symmetric_g2(ch2_timestamps, bin_width, max_delay)
bin_centers_hbt, hbt_values = compute_hbt_cross_correlation(ch1_timestamps, ch2_timestamps, bin_width, max_delay)

# Δt array
delta_ts = []
i = 0
j = 0
while i < len(ch1_timestamps) and j < len(ch2_timestamps):
    dt = ch2_timestamps[j] - ch1_timestamps[i]
    if abs(dt) <= max_delay:
        delta_ts.append(dt)
        i += 1
        j += 1
    elif dt < -max_delay:
        j += 1
    else:
        i += 1
delta_ts = np.array(delta_ts)
bin_centers_delta, g2_delta = compute_g2_of_deltas_fast(delta_ts, bin_width, max_delay)

# ----------------------------
# Plot All Four
# ----------------------------
plt.figure(figsize=(18, 8))

plt.subplot(2, 2, 1)
plt.plot(bin_centers_ch1 * 1e9, g2_ch1, color='blue')
plt.title(r"Ch1 $g^{(2)}(\tau)$ (Autocorrelation)", fontsize=14)
plt.xlabel(r"Delay $\tau$ (ns)")
plt.ylabel(r"$g^{(2)}(\tau)$")
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(bin_centers_ch2 * 1e9, g2_ch2, color='green')
plt.title(r"Ch2 $g^{(2)}(\tau)$ (Autocorrelation)", fontsize=14)
plt.xlabel(r"Delay $\tau$ (ns)")
plt.ylabel(r"$g^{(2)}(\tau)$")
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(bin_centers_hbt * 1e9, hbt_values, color='black')
plt.title(r"HBT: Ch1 $\leftrightarrow$ Ch2 Cross-Correlation", fontsize=14)
plt.xlabel(r"Time Delay $\tau$ (ns)")
plt.ylabel("Normalized Coincidence Rate")
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(bin_centers_delta * 1e9, g2_delta, color='purple')
plt.title(r"$g^{(2)}(\Delta t)$ for Ch2 - Ch1", fontsize=14)
plt.xlabel(r"Δt Delay Difference (ns)")
plt.ylabel(r"$g^{(2)}(\Delta t)$")
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)

plt.tight_layout()
plt.show()

# ----------------------------
# Analyze g²(0)
# ----------------------------
def analyze_g2_zero(bin_centers, g2_values, label):
    idx = np.argmin(np.abs(bin_centers))
    g2_zero = g2_values[idx]
    print(f"\n📊 g²(0) for {label} = {g2_zero:.3f}")
    if g2_zero < 1:
        print("🟢 Antibunched light (quantum, single-photon source)")
    elif np.isclose(g2_zero, 1, atol=0.05):
        print("🟡 Poissonian / Random (coherent laser)")
    else:
        print("🔴 Bunched light (thermal or classical source)")

analyze_g2_zero(bin_centers_ch1, g2_ch1, "Ch1")
analyze_g2_zero(bin_centers_ch2, g2_ch2, "Ch2")
analyze_g2_zero(bin_centers_hbt, hbt_values, "HBT (Ch1-Ch2)")
analyze_g2_zero(bin_centers_delta, g2_delta, "Δt (Ch2 - Ch1)")

