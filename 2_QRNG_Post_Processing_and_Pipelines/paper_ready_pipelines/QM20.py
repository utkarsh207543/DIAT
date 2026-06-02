import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. PARSE SPDC TIME-TAG DATA
# ============================================================

def parse_time_tags(filename):
    """
    Expected file format (per line):
    ch1_time   ch2_time
    Lines starting with % are ignored.
    Times are integers (TDC units).
    """
    ch1 = []
    ch2 = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue

            values = line.split()
            if len(values) < 2:
                continue

            try:
                t1 = int(values[0])
                t2 = int(values[1])
            except ValueError:
                continue

            ch1.append(t1)
            ch2.append(t2)

    return np.array(ch1), np.array(ch2)


# ============================================================
# 2. CERTIFIED ENTROPY VS COINCIDENCE WINDOW
# ============================================================

def entropy_time_duality(
    filename,
    time_unit=1e-12,     # seconds per TDC unit (change if needed)
    CAR=25,              # measured coincidence-to-accidental ratio
    W_min=20e-12,        # minimum coincidence window
    W_max=2e-9,          # maximum coincidence window
    N_windows=60,
    N_bins=50
):
    # Load time tags
    ch1, ch2 = parse_time_tags(filename)

    # Convert to seconds
    t1 = ch1 * time_unit
    t2 = ch2 * time_unit

    # Relative arrival times Δt
    delta_t = t1 - t2

    # Coincidence window sweep
    windows = np.linspace(W_min, W_max, N_windows)
    H_certified = []

    for W in windows:
        # Select coincidences inside window
        mask = np.abs(delta_t) < W / 2
        dt = delta_t[mask]

        # Not enough statistics
        if len(dt) < 200:
            H_certified.append(np.nan)
            continue

        # Histogram inside the window
        bins = np.linspace(-W/2, W/2, N_bins)
        hist, _ = np.histogram(dt, bins=bins, density=True)

        bin_width = bins[1] - bins[0]
        Pk = hist * bin_width
        P_max = np.max(Pk)

        # Worst-case single-pair fraction
        lambda_sp = CAR / (CAR + 1)

        # Certified min-entropy
        H = -np.log2(lambda_sp * P_max + (1 - lambda_sp))
        H_certified.append(H)

    return windows, np.array(H_certified)


# ============================================================
# 3. RUN ANALYSIS
# ============================================================

if __name__ == "__main__":

    INPUT_FILE = "Utkarsh_QRNG_10.txt"

    windows, H_cert = entropy_time_duality(
        filename=INPUT_FILE,
        time_unit=1e-12,   # <-- adjust if needed
        CAR=25             # <-- replace with your measured CAR
    )

    # ========================================================
    # 4. PLOT: ENTROPY–TIME DUALITY
    # ========================================================

    plt.figure(figsize=(7,5))
    plt.plot(windows * 1e12, H_cert, 'o-', lw=2)
    plt.xlabel("Coincidence window (ps)")
    plt.ylabel("Certified min-entropy (bits)")
    plt.title("Entropy–Time Duality in SPDC-Based QRNG")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ========================================================
    # 5. SAVE RESULTS
    # ========================================================

    np.savetxt(
        "entropy_time_duality.txt",
        np.column_stack([windows, H_cert]),
        header="Window(s)   Certified_MinEntropy(bits)"
    )

    print("✅ Analysis complete.")
    print("📁 Results saved to 'entropy_time_duality.txt'")
