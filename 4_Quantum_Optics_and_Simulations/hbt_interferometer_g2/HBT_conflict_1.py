import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Read timestamps from Moku:Lab CSV
# -----------------------------
def read_ch1_ch2(filename):
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

# -----------------------------
# Step 2: Cross-Correlation Histogram (HBT g²(τ))
# -----------------------------
def compute_cross_g2(ch1_times, ch2_times, bin_width=1e-9, max_delay=100e-9):
    delays = []

    for t1 in ch1_times:
        # Only look at ch2 events within ±max_delay of t1
        nearby_ch2 = ch2_times[(ch2_times > t1 - max_delay) & (ch2_times < t1 + max_delay)]
        delays.extend(nearby_ch2 - t1)

    if len(delays) == 0:
        print("⚠️ No valid coincidences found.")
        return [], []

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) > 0 else hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Step 3: Plot g²(τ) HBT-style
# -----------------------------
def plot_hbt_g2(tau, g2_vals):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2_vals, drawstyle='steps-mid', color='purple')
    plt.axvline(0, color='gray', linestyle='--', label="τ = 0")
    plt.title("Hanbury Brown and Twiss: Cross-Correlation g²(τ)")
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    g2_0 = g2_vals[np.argmin(np.abs(tau))] if len(tau) > 0 else 0
    print(f"g²(0) = {g2_0:.3f}")
    if g2_0 < 1:
        print("🟣 Antibunching (Single-photon behavior)")
    elif g2_0 > 1:
        print("🟡 Bunching (Thermal/Chaotic source)")
    else:
        print("⚪ Poissonian (Coherent/random source)")

# -----------------------------
# Main HBT Analysis
# -----------------------------
def hbt_pipeline(filename, bin_width=2e-9, max_delay=100e-9):
    print("📥 Reading Moku:Lab timestamp data...")
    ch1, ch2 = read_ch1_ch2(filename)
    print(f"✔️ Ch1 events: {len(ch1)} | Ch2 events: {len(ch2)}")

    print("📊 Computing cross-channel g²(τ)...")
    tau, g2 = compute_cross_g2(ch1, ch2, bin_width, max_delay)

    print("📈 Plotting HBT curve...")
    plot_hbt_g2(tau, g2)

# -----------------------------
# Run
# -----------------------------
hbt_pipeline("test5_bs.csv", bin_width=2e-9, max_delay=100e-9)
