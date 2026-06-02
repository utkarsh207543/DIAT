import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re

###############################################
# USER SETTINGS
###############################################

filename = "11.csv"

bin_width = 2e-9          # histogram bin width (2 ns)
max_delay = 200e-9        # correlation window ±200 ns
dead_time_ns = 45         # detector dead time (COUNT-series SPAD)

###############################################
# FILE PARSER (ROBUST FOR MOKU EXPORT)
###############################################

_SPLIT = re.compile(r"[,\t ]+")

def read_dual_channel_timestamps(filename):

    ch1 = []
    ch2 = []

    with open(filename, "r", encoding="utf-8", errors="ignore") as f:

        for line in f:

            s = line.strip()

            if not s or s.startswith('%'):
                continue

            parts = _SPLIT.split(s)

            if len(parts) < 2:
                continue

            try:
                src = int(parts[0])
                ts = float(parts[1])
            except:
                continue

            if src == 1:
                ch1.append(ts)

            elif src == 2:
                ch2.append(ts)

    return np.array(sorted(ch1)), np.array(sorted(ch2))


###############################################
# TRUE HBT CROSS-CORRELATION FUNCTION
###############################################

def compute_g2_cross(tA, tB, bin_width, max_delay):

    tA = np.asarray(tA)
    tB = np.asarray(tB)

    if len(tA) < 2 or len(tB) < 2:
        raise ValueError("Not enough timestamps for correlation.")

    T = min(tA[-1] - tA[0], tB[-1] - tB[0])

    RA = len(tA) / T
    RB = len(tB) / T

    print(f"Detector A rate: {RA:.2f} cps")
    print(f"Detector B rate: {RB:.2f} cps")

    edges = np.arange(-max_delay, max_delay + bin_width, bin_width)

    centers = 0.5 * (edges[:-1] + edges[1:])

    H = np.zeros(len(centers))

    j0 = 0

    for i in range(len(tA)):

        while j0 < len(tB) and tB[j0] < tA[i] - max_delay:
            j0 += 1

        j = j0

        while j < len(tB) and tB[j] <= tA[i] + max_delay:

            dt = tB[j] - tA[i]

            idx = int(np.floor((dt + max_delay) / bin_width))

            if 0 <= idx < len(H):
                H[idx] += 1

            j += 1

    g2 = H / (RA * RB * T * bin_width)

    return centers, g2


###############################################
# FIT MODEL
###############################################

def antibunching_model(tau, g0, tau_c):

    return 1 - (1 - g0) * np.exp(-np.abs(tau) / tau_c)


###############################################
# PLOT FUNCTION
###############################################

def plot_g2(tau, g2_vals):

    zero_index = np.argmin(np.abs(tau))

    g20 = g2_vals[zero_index]

    print(f"\nEstimated g²(0) = {g20:.3f}")

    if g20 < 1:
        print("Antibunching detected")
    elif g20 > 1:
        print("Bunching detected")
    else:
        print("Poissonian statistics")

    ###########################################

    try:

        popt, _ = curve_fit(
            antibunching_model,
            tau,
            g2_vals,
            bounds=([0, 0], [1, 1])
        )

        fit_success = True

    except:

        fit_success = False

    ###########################################

    plt.figure(figsize=(7,4))

    plt.plot(tau*1e9, g2_vals, drawstyle="steps-mid", label="Data")

    if fit_success:

        tau_fit = np.linspace(-max_delay, max_delay, 500)

        plt.plot(
            tau_fit*1e9,
            antibunching_model(tau_fit, *popt),
            'r',
            label="Fit"
        )

        print(f"Fitted g²(0) = {popt[0]:.3f}")
        print(f"Correlation time = {popt[1]*1e9:.2f} ns")

    plt.axhline(1, linestyle=":")

    plt.axvline(0, linestyle="--")

    plt.xlabel("Delay τ (ns)")

    plt.ylabel("g²(τ)")

    plt.title("HBT Second-Order Correlation Function")

    plt.legend()

    plt.grid(alpha=0.3)

    plt.tight_layout()

    plt.show()


###############################################
# MAIN PIPELINE
###############################################

def main():

    print("Reading timestamps from data.csv ...")

    tA, tB = read_dual_channel_timestamps(filename)

    print(f"Detector A events: {len(tA)}")

    print(f"Detector B events: {len(tB)}")

    tau, g2_vals = compute_g2_cross(
        tA,
        tB,
        bin_width,
        max_delay
    )

    plot_g2(tau, g2_vals)


###############################################
# RUN SCRIPT
###############################################

if __name__ == "__main__":

    main()