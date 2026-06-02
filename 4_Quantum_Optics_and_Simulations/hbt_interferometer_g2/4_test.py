import numpy as np
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm

# ----------------------------
# Parameters
# ----------------------------
filename = "test_2ch.csv"  # Replace with your actual file
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
# g²(τ) computation
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
            delays.append(-dt)  # for symmetry
    delays = np.array(delays)

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, _ = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) != 0 else hist
    bin_centers = (bins[:-1] + bins[1:]) / 2
    return bin_centers, g2

# Compute for Ch1
bin_centers_ch1, g2_ch1 = compute_symmetric_g2(ch1_timestamps, bin_width, max_delay)

# Compute for Ch2
bin_centers_ch2, g2_ch2 = compute_symmetric_g2(ch2_timestamps, bin_width, max_delay)

# ----------------------------
# Plotting
# ----------------------------
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(bin_centers_ch1 * 1e9, g2_ch1, color='blue')
plt.title(r"$g^{(2)}(\tau)$ for Ch1", fontsize=14)
plt.xlabel(r"Time Delay $\tau$ (ns)")
plt.ylabel(r"$g^{(2)}(\tau)$")
plt.axvline(0, linestyle='--', color='gray')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(bin_centers_ch2 * 1e9, g2_ch2, color='green')
plt.title(r"$g^{(2)}(\tau)$ for Ch2", fontsize=14)
plt.xlabel(r"Time Delay $\tau$ (ns)")
plt.ylabel(r"$g^{(2)}(\tau)$")
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
