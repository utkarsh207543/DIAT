import numpy as np
import matplotlib.pyplot as plt
import os


# -----------------------------
# Read timestamps from Moku:Lab CSV
# -----------------------------
def read_ch1_ch2_timestamps(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ File not found: {filename}")

    ch1, ch2 = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('%') or not line.strip():
                continue
            try:
                source, timestamp = line.strip().split(',')
                timestamp = float(timestamp.strip())
                if int(source.strip()) == 1:
                    ch1.append(timestamp)
                elif int(source.strip()) == 2:
                    ch2.append(timestamp)
            except ValueError:
                continue

    ch1 = np.array(sorted(ch1))
    ch2 = np.array(sorted(ch2))
    print(f"✔️ Ch1 count: {len(ch1)} | Ch2 count: {len(ch2)}")
    print("🔍 First 10 Ch1:", ch1[:10])
    print("🔍 First 10 Ch2:", ch2[:10])
    return ch1, ch2


# -----------------------------
# Efficient symmetric g²(τ)
# -----------------------------
def compute_symmetric_g2_fast(timestamps, bin_width, max_delay):
    delays = []
    for i, t in enumerate(timestamps):
        start = np.searchsorted(timestamps, t - max_delay, side='left')
        end = np.searchsorted(timestamps, t + max_delay, side='right')
        neighbors = timestamps[start:end]
        local_deltas = neighbors - t
        local_deltas = local_deltas[local_deltas != 0]
        delays.extend(local_deltas)
    if not delays:
        print("⚠️ No time differences found.")
        return [], []
    delays = np.array(delays)
    print(f"⏱️ Total delays (self): {len(delays)}")
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, edges = np.histogram(delays, bins=bins)
    tau = edges[:-1] + bin_width / 2
    g2 = hist / np.mean(hist) if np.mean(hist) > 0 else hist
    return tau, g2


# -----------------------------
# Cross-channel g²(τ)
# -----------------------------
def compute_cross_g2_fast(ch1, ch2, bin_width, max_delay):
    delays = []
    for t1 in ch1:
        start = np.searchsorted(ch2, t1 - max_delay, side='left')
        end = np.searchsorted(ch2, t1 + max_delay, side='right')
        nearby = ch2[start:end]
        delays.extend(nearby - t1)
    if not delays:
        print("⚠️ No coincidences found.")
        return [], []
    delays = np.array(delays)
    print(f"⏱️ Total delays (cross): {len(delays)}")
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, edges = np.histogram(delays, bins=bins)
    tau = edges[:-1] + bin_width / 2
    g2 = hist / np.mean(hist) if np.mean(hist) > 0 else hist
    return tau, g2


# -----------------------------
# Plotting
# -----------------------------
def plot_g2(tau, g2, label="g²(τ)", zoom_ns=None):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2, drawstyle='steps-mid')
    plt.axvline(0, color='gray', linestyle='--', label="τ = 0")
    plt.title(label)
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    if zoom_ns:
        plt.xlim(-zoom_ns, zoom_ns)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    g2_0 = g2[np.argmin(np.abs(tau))] if len(tau) else 0
    return g2_0


# -----------------------------
# Interpretation
# -----------------------------
def classify_g2(g2_0, label=""):
    print(f"\n📌 {label} → g²(0) = {g2_0:.3f}")
    if g2_0 < 0.95:
        print("🟣 Antibunching: Sub-Poissonian (quantum light, single-photon source)")
    elif g2_0 > 1.05:
        print("🟡 Bunching: Super-Poissonian (thermal/chaotic light)")
    else:
        print("⚪ Poissonian: Coherent light (e.g., laser)")


# -----------------------------
# Main HBT Pipeline
# -----------------------------
def full_g2_pipeline(filename, bin_width=50e-9, max_delay=1e-6, zoom_ns=500):
    print("📥 Loading data...")
    ch1, ch2 = read_ch1_ch2_timestamps(filename)

    if len(ch1) < 10 or len(ch2) < 10:
        print("❌ Not enough data.")
        return

    print("\n🔁 Ch1 autocorrelation...")
    tau1, g2_1 = compute_symmetric_g2_fast(ch1, bin_width, max_delay)
    g2_0_ch1 = plot_g2(tau1, g2_1, label="Ch1 g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_ch1, "Ch1")

    print("\n🔁 Ch2 autocorrelation...")
    tau2, g2_2 = compute_symmetric_g2_fast(ch2, bin_width, max_delay)
    g2_0_ch2 = plot_g2(tau2, g2_2, label="Ch2 g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_ch2, "Ch2")

    print("\n🔁 Cross-correlation (Ch1 ↔ Ch2)...")
    tau_c, g2_c = compute_cross_g2_fast(ch1, ch2, bin_width, max_delay)
    g2_0_cross = plot_g2(tau_c, g2_c, label="Ch1–Ch2 HBT g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_cross, "Ch1–Ch2")


# -----------------------------
# Run the pipeline
# -----------------------------
# Replace filename with your actual CSV file name
full_g2_pipeline("test4.csv", bin_width=50e-9, max_delay=1e-6, zoom_ns=500)
