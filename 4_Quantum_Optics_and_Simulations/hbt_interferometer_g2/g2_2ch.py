import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Read timestamps for both channels
# -----------------------------
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

# -----------------------------
# Step 2: Compute G²
# -----------------------------
def compute_g2(timestamps, bin_width=1e-9, max_delay=1e-6):
    time_diffs = []
    for i in range(len(timestamps)):
        for j in range(i + 1, len(timestamps)):
            dt = timestamps[j] - timestamps[i]
            if dt > max_delay:
                break
            time_diffs.append(dt)

    if len(time_diffs) == 0:
        print("⚠️ No valid time differences found. Try increasing max_delay.")
        return [], []

    bins = np.arange(0, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(time_diffs, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) != 0 else hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Step 3: Plot G²
# -----------------------------
def plot_g2_dual(tau1, g2_1, tau2, g2_2):
    plt.figure(figsize=(10, 5))

    # Channel 1
    plt.subplot(1, 2, 1)
    plt.plot(tau1 * 1e9, g2_1, drawstyle='steps-mid')
    plt.title("g²(τ) - Ch1")
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.grid(True)

    # Channel 2
    plt.subplot(1, 2, 2)
    plt.plot(tau2 * 1e9, g2_2, drawstyle='steps-mid', color='orange')
    plt.title("g²(τ) - Ch2")
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# -----------------------------
# Step 4: Interpret G²(0)
# -----------------------------
def analyze_g2(g2_vals, label=""):
    if len(g2_vals) == 0:
        print(f"{label}: ❌ No valid g² data.")
        return
    g2_0 = g2_vals[0]
    print(f"{label} → g²(0) = {g2_0:.3f}")
    if g2_0 < 1:
        print("🟣 Antibunching: Likely single-photon source")
    elif g2_0 > 1:
        print("🟡 Bunching: Thermal/chaotic light")
    else:
        print("⚪ Random/Poissonian source")

# -----------------------------
# MAIN
# -----------------------------
def g2_dual_pipeline(filename, bin_width=2e-9, max_delay=100e-9):
    print("📥 Reading timestamps from Ch1 and Ch2...")
    ch1_times, ch2_times = read_channel_timestamps(filename)
    print(f"✔️ Ch1: {len(ch1_times)} events | Ch2: {len(ch2_times)} events")

    print("\n📊 Computing g²(τ) for Ch1...")
    tau1, g2_1 = compute_g2(ch1_times, bin_width, max_delay)

    print("\n📊 Computing g²(τ) for Ch2...")
    tau2, g2_2 = compute_g2(ch2_times, bin_width, max_delay)

    print("\n📈 Plotting...")
    plot_g2_dual(tau1, g2_1, tau2, g2_2)

    print("\n📡 Interpretation:")
    analyze_g2(g2_1, "Ch1")
    analyze_g2(g2_2, "Ch2")

# -----------------------------
# Run
# -----------------------------
g2_dual_pipeline("test5_bs.csv", bin_width=2e-9, max_delay=100e-9)
