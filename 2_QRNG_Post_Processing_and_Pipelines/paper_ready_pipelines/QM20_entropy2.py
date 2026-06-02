import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

# ============================================================
# 1. PARSE SPDC TIME-TAG DATA
# ============================================================

def parse_time_tags(filename):
    ch1, ch2 = [], []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue

            vals = line.split()
            if len(vals) < 2:
                continue

            try:
                t1 = int(vals[0])
                t2 = int(vals[1])
            except ValueError:
                continue

            ch1.append(t1)
            ch2.append(t2)

    return np.array(ch1), np.array(ch2)


# ============================================================
# 2. VON NEUMANN DEBIASING
# ============================================================

def von_neumann(bits):
    out = []
    i = 0
    while i < len(bits) - 1:
        if bits[i] != bits[i+1]:
            out.append(bits[i+1])
        i += 2
    return np.array(out)


# ============================================================
# 3. ENTROPY–TIME DUALITY + VN CHECK
# ============================================================

def entropy_time_duality_with_vn(
    filename,
    time_unit=1e-12,
    CAR=25,
    W_min=20e-12,
    W_max=2e-9,
    N_windows=60,
    N_bins=50
):
    ch1, ch2 = parse_time_tags(filename)

    t1 = ch1 * time_unit
    t2 = ch2 * time_unit
    delta_t = t1 - t2

    windows = np.linspace(W_min, W_max, N_windows)

    H_cert_norm = []
    H_post_vn = []
    VN_efficiency = []

    H_max = np.log2(N_bins)

    for W in windows:
        mask = np.abs(delta_t) < W / 2
        dt = delta_t[mask]

        if len(dt) < 500:
            H_cert_norm.append(np.nan)
            H_post_vn.append(np.nan)
            VN_efficiency.append(np.nan)
            continue

        # ---------- PHYSICAL CERTIFIED ENTROPY ----------
        bins = np.linspace(-W/2, W/2, N_bins)
        hist, _ = np.histogram(dt, bins=bins, density=True)
        Pk = hist * (bins[1] - bins[0])
        Pmax = np.max(Pk)

        lambda_sp = CAR / (CAR + 1)
        H_cert = -np.log2(lambda_sp * Pmax + (1 - lambda_sp))
        H_cert_norm.append(H_cert / H_max)

        # ---------- BIT GENERATION ----------
        raw_bits = (dt >= 0).astype(int)

        # ---------- VON NEUMANN ----------
        vn_bits = von_neumann(raw_bits)
        VN_efficiency.append(len(vn_bits) / len(raw_bits))

        if len(vn_bits) < 100:
            H_post_vn.append(np.nan)
        else:
            p = np.bincount(vn_bits, minlength=2) / len(vn_bits)
            H_post_vn.append(entropy(p, base=2))

    return windows, np.array(H_cert_norm), np.array(H_post_vn), np.array(VN_efficiency)


# ============================================================
# 4. RUN ANALYSIS
# ============================================================

if __name__ == "__main__":

    windows, H_phys, H_vn, eff = entropy_time_duality_with_vn(
        filename="Utkarsh_QRNG_10.txt",
        CAR=25
    )

    # ========================================================
    # 5. PLOTS
    # ========================================================

    fig, ax = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

    # (a) Physical entropy
    ax[0].plot(windows * 1e12, H_phys, 'o-')
    ax[0].set_ylabel("Normalized certified entropy")
    ax[0].set_ylim(0, 1)
    ax[0].set_title("Physical Entropy–Time Duality")

    # (b) Post-VN entropy
    ax[1].plot(windows * 1e12, H_vn, 'o-', color='green')
    ax[1].set_ylabel("Shannon entropy after VN")
    ax[1].set_ylim(0, 1)
    ax[1].set_title("Entropy After Von Neumann Debiasing")

    # (c) VN efficiency
    ax[2].plot(windows * 1e12, eff, 'o-', color='red')
    ax[2].set_ylabel("VN efficiency")
    ax[2].set_xlabel("Coincidence window (ps)")
    ax[2].set_title("Von Neumann Extraction Efficiency")

    for a in ax:
        a.grid(True)

    plt.tight_layout()
    plt.show()
