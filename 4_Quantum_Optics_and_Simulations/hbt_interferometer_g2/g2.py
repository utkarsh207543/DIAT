import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Step 1: Read Ch1 timestamps from Moku:Lab CSV
# -----------------------------
def read_ch1_timestamps(filename):
    timestamps = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            try:
                source, timestamp = line.split(',')
                if int(source.strip()) == 1:
                    timestamps.append(float(timestamp.strip()))
            except ValueError:
                continue
    return np.array(sorted(timestamps))

# -----------------------------
# Step 2: Compute G2 Histogram
# -----------------------------
def compute_g2(timestamps, bin_width=1e-9, max_delay=1e-6):
    time_diffs = []

    for i in range(len(timestamps)):
        for j in range(i + 1, len(timestamps)):
            delta = timestamps[j] - timestamps[i]
            if delta > max_delay:
                break
            time_diffs.append(delta)

    time_diffs = np.array(time_diffs)
    bins = np.arange(0, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(time_diffs, bins=bins)
    g2 = hist / np.mean(hist)  # Normalize to mean = 1
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2

# -----------------------------
# Step 3: Plot G2
# -----------------------------
def plot_g2(tau, g2_vals):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2_vals, drawstyle='steps-mid')
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.title("Second-Order Correlation Function g²(τ)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------
# Step 4: Analyze G2(0)
# -----------------------------
def analyze_g2(g2_vals):
    g2_zero = g2_vals[0]
    print(f"🔍 g²(0) = {g2_zero:.3f}")
    if g2_zero < 1:
        print("🟣 Antibunching: Quantum (sub-Poissonian) source")
    elif g2_zero > 1:
        print("🟡 Bunching: Thermal (super-Poissonian) source")
    else:
        print("⚪ Poissonian: Coherent/random source")

# -----------------------------
# MAIN
# -----------------------------
def g2_pipeline(input_file, bin_width=1e-9, max_delay=1e-6):
    print("📥 Reading Ch1 timestamps...")
    timestamps = read_ch1_timestamps(input_file)
    print(f"✔️ Loaded {len(timestamps)} Ch1 timestamps")

    print("📊 Computing g²(τ)...")
    tau, g2_vals = compute_g2(timestamps, bin_width, max_delay)

    print("📈 Plotting...")
    plot_g2(tau, g2_vals)

    print("📡 Interpreting g²(0)...")
    analyze_g2(g2_vals)

# -----------------------------
# Run the pipeline
# -----------------------------
g2_pipeline("test.csv", bin_width=2e-9, max_delay=100e-9)
