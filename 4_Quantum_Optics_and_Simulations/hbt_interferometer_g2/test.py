import numpy as np
import matplotlib.pyplot as plt


# -----------------------------
# Step 1: Read Ch1 timestamps
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
# Step 2: Compute g2(τ)
# -----------------------------
def compute_g2(timestamps, bin_width=1e-9, max_delay=1e-6):
    time_diffs = []
    j = 0
    for i in range(len(timestamps)):
        while j < len(timestamps) and timestamps[j] - timestamps[i] <= max_delay:
            if i != j:
                time_diffs.append(timestamps[j] - timestamps[i])
            j += 1
        j = i + 1
    time_diffs = np.array(time_diffs)
    bins = np.arange(0, max_delay + bin_width, bin_width)
    hist, bin_edges = np.histogram(time_diffs, bins=bins)
    mean_hist = np.mean(hist) if np.mean(hist) != 0 else 1
    g2 = hist / mean_hist
    tau = bin_edges[:-1] + bin_width / 2
    return tau, g2


# -----------------------------
# Step 3: Photon arrival pattern
# -----------------------------
def simulate_photon_arrival(timestamps, N=30):
    first_ts = timestamps[:N]
    intervals = np.diff(first_ts)
    return intervals


# -----------------------------
# Step 4: Photon count histogram (optimized)
# -----------------------------
def photon_count_histogram(timestamps, num_bins=1000):
    min_t = np.min(timestamps)
    max_t = np.max(timestamps)
    bins = np.linspace(min_t, max_t, num_bins + 1)
    counts, _ = np.histogram(timestamps, bins=bins)
    return counts


# -----------------------------
# Step 5: Classification
# -----------------------------
def classify_vmr(counts):
    mean_c = np.mean(counts)
    var_c = np.var(counts)
    vmr = var_c / mean_c if mean_c != 0 else 0
    if vmr < 1:
        return "Sub-Poissonian", vmr
    elif np.isclose(vmr, 1, atol=0.05):
        return "Poissonian", vmr
    else:
        return "Super-Poissonian", vmr


# -----------------------------
# Step 6: Combined Plot
# -----------------------------
def combined_plot(tau, g2_vals, intervals, counts, stat_label, vmr):
    fig, axs = plt.subplots(3, 1, figsize=(8, 10))

    # Plot g²(τ)
    axs[0].plot(tau * 1e9, g2_vals, drawstyle='steps-mid')
    axs[0].axvline(0, color='red', linestyle='--', label='τ = 0')
    axs[0].set_title(f"g²(τ): {stat_label} (VMR = {vmr:.2f})")
    axs[0].set_xlabel("Delay τ (ns)")
    axs[0].set_ylabel("g²(τ)")
    axs[0].legend()
    axs[0].grid(True)

    # Photon arrival pattern
    arrival_line = np.cumsum(np.insert(intervals, 0, 0))
    axs[1].eventplot(arrival_line, colors='red')
    axs[1].set_title("Simulated Photon Arrival (First 30 Events)")
    axs[1].set_xlabel("Time (arb. units)")
    axs[1].set_yticks([])

    # Photon count histogram
    axs[2].hist(counts, bins=50, color='gray', edgecolor='black')
    axs[2].set_title("Photon Count Distribution")
    axs[2].set_xlabel("Photon counts per bin")
    axs[2].set_ylabel("Frequency")

    plt.tight_layout()
    plt.show()


# -----------------------------
# Main Execution
# -----------------------------
def run_full_pipeline(input_file):
    timestamps = read_ch1_timestamps(input_file)
    tau, g2_vals = compute_g2(timestamps)
    intervals = simulate_photon_arrival(timestamps)
    counts = photon_count_histogram(timestamps)
    stat_label, vmr = classify_vmr(counts)
    combined_plot(tau, g2_vals, intervals, counts, stat_label, vmr)

# Example usage
run_full_pipeline("test.csv")  # Replace with your actual CSV file name
