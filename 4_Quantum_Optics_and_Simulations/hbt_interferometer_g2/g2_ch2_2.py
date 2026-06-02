import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Read timestamps from file
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
# Step 2: Compute symmetric g²(τ)
# -----------------------------
def compute_symmetric_g2(timestamps, bin_width=1e-9, max_delay=1e-6):
    time_diffs = []

    for i in range(len(timestamps)):
        for j in range(len(timestamps)):
            if i == j:
                continue
            delta = timestamps[j] - timestamps[i]
            if abs(delta) <= max_delay:
                time_diffs.append(delta)

    if len(time_diffs) == 0:
        print("⚠️ No valid time differences. Try increasing max_delay.")
        return [], []

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(time_diffs, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) != 0 else hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Step 3: Plot g²(τ) with label
# -----------------------------
def plot_g2(tau, g2_vals, label="Channel", zoom_ns=None):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2_vals, drawstyle='steps-mid')
    plt.axvline(0, color='gray', linestyle='--', label="τ = 0")
    g2_0 = g2_vals[np.argmin(np.abs(tau))] if len(tau) > 0 else 0
    plt.title(f"Second-Order Correlation g²(τ) - {label}")
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.grid(True)
    plt.legend()
    if zoom_ns:
        plt.xlim(-zoom_ns, zoom_ns)
    plt.tight_layout()
    plt.show()
    return g2_0

# -----------------------------
# Step 4: Interpret g²(0)
# -----------------------------
def interpret_g2(g2_0, label=""):
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
def g2_symmetric_pipeline(filename, bin_width=1e-9, max_delay=1e-6, zoom_ns=50):
    print("📥 Reading timestamps...")
    ch1_times, ch2_times = read_channel_timestamps(filename)
    print(f"✔️ Ch1 events: {len(ch1_times)} | Ch2 events: {len(ch2_times)}")

    print("\n📊 Computing g²(τ) for Ch1 (symmetric)...")
    tau1, g2_1 = compute_symmetric_g2(ch1_times, bin_width, max_delay)
    g2_0_ch1 = plot_g2(tau1, g2_1, label="Ch1", zoom_ns=zoom_ns)
    interpret_g2(g2_0_ch1, label="Ch1")

    print("\n📊 Computing g²(τ) for Ch2 (symmetric)...")
    tau2, g2_2 = compute_symmetric_g2(ch2_times, bin_width, max_delay)
    g2_0_ch2 = plot_g2(tau2, g2_2, label="Ch2", zoom_ns=zoom_ns)
    interpret_g2(g2_0_ch2, label="Ch2")

# -----------------------------
# Run the pipeline
# -----------------------------
g2_symmetric_pipeline("test3.csv", bin_width=2e-9, max_delay=100e-9, zoom_ns=20)
