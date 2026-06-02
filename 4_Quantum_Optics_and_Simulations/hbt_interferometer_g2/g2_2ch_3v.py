import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------- STEP 1: Read from CSV --------
def read_channel_timestamps(filename):
    df = pd.read_csv(filename, comment='%')
    df.columns = [col.strip() for col in df.columns]

    if len(df.columns) < 2:
        raise ValueError("CSV must have at least two columns: Source, Timestamp")

    source_col = df.columns[0]
    time_col = df.columns[1]

    ch1 = df[df[source_col] == 1][time_col].values
    ch2 = df[df[source_col] == 2][time_col].values

    return np.sort(ch1), np.sort(ch2)

# -------- STEP 2: g2 Calculation --------
def compute_g2(start_times, stop_times, bin_width=1e-6, max_delay=5e-5):
    delays = []
    i = 0
    j = 0
    stop_len = len(stop_times)

    for t1 in start_times:
        while j < stop_len and stop_times[j] < t1 - max_delay:
            j += 1
        k = j
        while k < stop_len and stop_times[k] <= t1 + max_delay:
            delays.append(stop_times[k] - t1)
            k += 1

    delays = np.array(delays)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, edges = np.histogram(delays, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2

    # Normalize
    norm = (len(start_times) * bin_width)
    g2 = hist / norm if norm != 0 else hist
    return centers, g2

# -------- STEP 3: Plot g2 --------
def plot_g2(centers, g2, title):
    plt.figure(figsize=(8, 4))
    plt.plot(centers * 1e6, g2)  # Convert to μs
    plt.title(f"g²(τ) - {title}")
    plt.xlabel("Delay τ [μs]")
    plt.ylabel("g²(τ)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -------- STEP 4: Display g2 Table --------
def print_g2_values(centers, g2, label):
    print(f"\n📊 g²(τ) values for {label}")
    print(f"{'Delay (μs)':>15} | {'g²(τ)':>10}")
    print("-" * 30)
    for tau, g in zip(centers * 1e6, g2):
        print(f"{tau:>15.3f} | {g:>10.5f}")

# -------- STEP 5: Get g2 at τ=0 --------
def g2_zero(centers, g2):
    idx = np.argmin(np.abs(centers))
    return g2[idx]

# -------- MAIN --------
def run_full_pipeline(filename):
    ch1, ch2 = read_channel_timestamps(filename)
    print(f"✔️ Ch1 count: {len(ch1)} | Ch2 count: {len(ch2)}")

    # Ch1–Ch1
    centers, g2 = compute_g2(ch1, ch1)
    print_g2_values(centers, g2, "Ch1–Ch1")
    plot_g2(centers, g2, "Ch1–Ch1")
    g2_ch1 = g2_zero(centers, g2)

    # Ch2–Ch2
    centers, g2 = compute_g2(ch2, ch2)
    print_g2_values(centers, g2, "Ch2–Ch2")
    plot_g2(centers, g2, "Ch2–Ch2")
    g2_ch2 = g2_zero(centers, g2)

    # Ch1–Ch2
    centers, g2 = compute_g2(ch1, ch2)
    print_g2_values(centers, g2, "Ch1–Ch2")
    plot_g2(centers, g2, "Ch1–Ch2")
    g2_cross = g2_zero(centers, g2)

    # -------- Final Summary --------
    print("\n📌 Final g²(0) Results:")
    print(f"g2 Ch1–Ch1 = {g2_ch1:.5f}")
    print(f"g2 Ch2–Ch2 = {g2_ch2:.5f}")
    print(f"g2 Ch1–Ch2 = {g2_cross:.5f}")

# -------- RUN --------
if __name__ == "__main__":
    run_full_pipeline("test5_bs.csv")  # Replace with your actual file

