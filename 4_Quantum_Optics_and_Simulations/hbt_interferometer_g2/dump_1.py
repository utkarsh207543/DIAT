import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv
from tqdm import tqdm

# ----------------------------
# Parameters
# ----------------------------
filename = "test_2ch.csv"  # Replace with your actual uploaded file path
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

# Truncate to equal length
min_len = min(len(ch1_timestamps), len(ch2_timestamps))
ch1_timestamps = ch1_timestamps[:min_len]
ch2_timestamps = ch2_timestamps[:min_len]

print(f"✂️ Truncated to same length: {min_len} entries each")

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
    return bin_centers, g2, hist

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
    return bin_centers, norm_hist, hist

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
    return delays[mask], g2[mask], counts

# ----------------------------
# Compute All
# ----------------------------
bin_centers_ch1, g2_ch1, hist_ch1 = compute_symmetric_g2(ch1_timestamps, bin_width, max_delay)
bin_centers_ch2, g2_ch2, hist_ch2 = compute_symmetric_g2(ch2_timestamps, bin_width, max_delay)
bin_centers_hbt, hbt_values, hist_hbt = compute_hbt_cross_correlation(ch1_timestamps, ch2_timestamps, bin_width, max_delay)

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
bin_centers_delta, g2_delta, delta_counts = compute_g2_of_deltas_fast(delta_ts, bin_width, max_delay)

# ----------------------------
# Visual Summary Plot
# ----------------------------
fig, axes = plt.subplots(3, 4, figsize=(20, 8))
plt.subplots_adjust(hspace=0.8, wspace=0.4)

def interpret_g2(g2_zero):
    if g2_zero < 1:
        return "🟢 g²(0)<1 (Antibunched)"
    elif np.isclose(g2_zero, 1, atol=0.05):
        return "🟡 g²(0)≈1 (Random)"
    else:
        return "🔴 g²(0)>1 (Bunched)"

def plot_summary(i, label, bin_centers, g2, counts, timestamps):
    idx_zero = np.argmin(np.abs(bin_centers))
    g2_zero = g2[idx_zero]
    interpretation = interpret_g2(g2_zero)

    # g2(τ)
    axes[0, i].plot(bin_centers * 1e9, g2, color='black')
    axes[0, i].set_title(f"{label}\n$g^{(2)}(0)$ = {g2_zero:.3f}\n{interpretation}")
    axes[0, i].set_xlabel("τ (ns)")
    axes[0, i].set_ylabel("$g^{(2)}(\\tau)$")
    axes[0, i].axvline(0, linestyle='--', color='gray')
    axes[0, i].grid(True)

    # Photon arrival raster
    axes[1, i].eventplot(timestamps[:20], colors='black')
    axes[1, i].set_title(f"Photon Arrival Raster\n{interpretation}")
    axes[1, i].set_yticks([])
    axes[1, i].set_xticks([])

    # Histogram of photon counts
    sns.histplot(counts, bins=50, ax=axes[2, i], color='black')
    axes[2, i].set_title("Photon Count Histogram")
    axes[2, i].set_xlabel("Photon counts")
    axes[2, i].set_ylabel("Frequency")

plot_summary(0, "Ch1", bin_centers_ch1, g2_ch1, hist_ch1, ch1_timestamps)
plot_summary(1, "Ch2", bin_centers_ch2, g2_ch2, hist_ch2, ch2_timestamps)
plot_summary(2, "HBT Ch1↔Ch2", bin_centers_hbt, hbt_values, hist_hbt, delta_ts)
plot_summary(3, "Δt (Ch2 - Ch1)", bin_centers_delta, g2_delta, delta_counts, delta_ts)

plt.tight_layout()
plt.show()
