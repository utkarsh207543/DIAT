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
# 2. ENTROPY–TIME DUALITY WITH NORMALIZATION
# ============================================================

def entropy_time_duality_normalized(
    filename,
    time_unit=1e-12,     # seconds per TDC unit
    CAR=25,              # measured coincidence-to-accidental ratio
    W_min=20e-12,
    W_max=2e-9,
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
    H_normalized = []

    H_max = np.log2(N_bins)  # maximum possible min-entropy

    for W in windows:
        # Select coincidences within window
        mask = np.abs(delta_t) < W / 2
        dt = delta_t[mask]

        if len(dt) < 200:
            H_certified.append(np.nan)
            H_normalized.append(np.nan)
            continue

        # Histogram
        bins = np.linspace(-W/2, W/2, N_bins)
        hist, _ = np.histogram(dt, bins=bins, density=True)

        bin_width = bins[1] - bins[0]
        Pk = hist * bin_width
        P_max = np.max(Pk)

        # Worst-case single-pair fraction
        lambda_sp = CAR / (CAR + 1)

        # Certified min-entropy
        H = -np.log2(lambda_sp * P_max + (1 - lambda_sp))

        # Normalized entropy (0–1)
        H_norm = H / H_max

        H_certified.append(H)
        H_normalized.append(H_norm)

    return windows, np.array(H_certified), np.array(H_normalized)


# ============================================================
# 3. RUN ANALYSIS
# ============================================================

if __name__ == "__main__":

    INPUT_FILE = "Utkarsh_QRNG_10.txt"

    windows, H_raw, H_norm = entropy_time_duality_normalized(
        filename=INPUT_FILE,
        time_unit=1e-12,   # adjust if your TDC unit is different
        CAR=25             # replace with your measured CAR
    )

    # ========================================================
    # 4. PLOT RESULTS
    # ========================================================

    plt.figure(figsize=(8,5))
    plt.plot(windows * 1e12, H_norm, 'o-', lw=2)
    plt.xlabel("Coincidence window (ps)")
    plt.ylabel("Normalized certified entropy (0–1)")
    plt.title("Entropy–Time Duality in SPDC-Based QRNG")
    plt.ylim(0, 1.05)
    plt.grid(True)

    # Quality regions (optional but very nice for papers)
    plt.axhspan(0.9, 1.0, color='green', alpha=0.1, label="Excellent")
    plt.axhspan(0.7, 0.9, color='yellow', alpha=0.1, label="Good")
    plt.axhspan(0.0, 0.4, color='red', alpha=0.05, label="Poor")

    plt.legend()
    plt.tight_layout()
    plt.show()

    # ========================================================
    # 5. SAVE RESULTS
    # ========================================================

    np.savetxt(
        "entropy_time_duality_normalized.txt",
        np.column_stack([windows, H_raw, H_norm]),
        header="Window(s)   Certified_MinEntropy(bits)   Normalized_Entropy(0-1)"
    )

    print("✅ Analysis complete")
    print("📁 Results saved to 'entropy_time_duality_normalized.txt'")
