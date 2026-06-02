import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Read Moku:Lab CSV timestamps
# -----------------------------
def read_ch1_ch2_timestamps(filename):
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
# Efficient symmetric g²(τ)
# -----------------------------
def compute_symmetric_g2_fast(timestamps, bin_width=1e-9, max_delay=1e-6):
    timestamps = np.sort(timestamps)
    delays = []

    for i, t in enumerate(timestamps):
        start = np.searchsorted(timestamps, t - max_delay, side='left')
        end = np.searchsorted(timestamps, t + max_delay, side='right')
        neighbors = timestamps[start:end]
        local_deltas = neighbors - t
        local_deltas = local_deltas[local_deltas != 0]
        delays.extend(local_deltas)

    if not delays:
        return [], []

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) else hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Efficient cross-channel g²(τ)
# -----------------------------
def compute_cross_g2_fast(ch1, ch2, bin_width=1e-9, max_delay=1e-6):
    ch1 = np.sort(ch1)
    ch2 = np.sort(ch2)
    delays = []

    for t1 in ch1:
        start = np.searchsorted(ch2, t1 - max_delay, side='left')
        end = np.searchsorted(ch2, t1 + max_delay, side='right')
        tau = ch2[start:end] - t1
        delays.extend(tau)

    if not delays:
        return [], []

    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(delays, bins=bins)
    g2 = hist / np.mean(hist) if np.mean(hist) else hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Classification
# -----------------------------
def classify_g2(g2_0, label=""):
    print(f"\n📌 {label} → g²(0) = {g2_0:.3f}")
    if g2_0 < 0.95:
        print("🟣 Antibunching detected!")
        print("📌 Interpretation: Quantum emitter (e.g. single-photon source)")
        print("📊 Statistical model: Sub-Poissonian")
    elif 0.95 <= g2_0 <= 1.05:
        print("⚪ Poissonian light detected!")
        print("📌 Interpretation: Coherent source (e.g. laser)")
        print("📊 Statistical model: Poissonian")
    elif g2_0 > 1.05:
        print("🟡 Bunching detected!")
        print("📌 Interpretation: Thermal or chaotic light source")
        print("📊 Statistical model: Super-Poissonian")
    else:
        print("❓ Unable to classify")

# -----------------------------
# Plotting utility
# -----------------------------
def plot_g2(tau, g2_vals, label="g²(τ)", zoom_ns=50):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2_vals, drawstyle='steps-mid')
    plt.axvline(0, color='gray', linestyle='--')
    plt.title(f"{label}")
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.xlim(-zoom_ns, zoom_ns)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    g2_0 = g2_vals[np.argmin(np.abs(tau))] if len(tau) else 0
    return g2_0

# -----------------------------
# Main classification pipeline
# -----------------------------
def full_g2_classification_pipeline(filename, bin_width=2e-9, max_delay=100e-9, zoom_ns=20):
    print("📥 Loading timestamp data...")
    ch1, ch2 = read_ch1_ch2_timestamps(filename)
    print(f"✔️ Ch1: {len(ch1)} events | Ch2: {len(ch2)} events")

    print("\n🔁 Computing g²(τ) for Ch1...")
    tau1, g2_1 = compute_symmetric_g2_fast(ch1, bin_width, max_delay)
    g2_0_ch1 = plot_g2(tau1, g2_1, label="Ch1: g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_ch1, "Ch1")

    print("\n🔁 Computing g²(τ) for Ch2...")
    tau2, g2_2 = compute_symmetric_g2_fast(ch2, bin_width, max_delay)
    g2_0_ch2 = plot_g2(tau2, g2_2, label="Ch2: g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_ch2, "Ch2")

    print("\n🔁 Computing cross-channel g²(τ)...")
    tau_cross, g2_cross = compute_cross_g2_fast(ch1, ch2, bin_width, max_delay)
    g2_0_cross = plot_g2(tau_cross, g2_cross, label="Ch1-Ch2 HBT g²(τ)", zoom_ns=zoom_ns)
    classify_g2(g2_0_cross, "Ch1-Ch2")

# -----------------------------
# Run the full pipeline
# -----------------------------
full_g2_classification_pipeline("test3.csv", bin_width=2e-9, max_delay=100e-9, zoom_ns=20)
