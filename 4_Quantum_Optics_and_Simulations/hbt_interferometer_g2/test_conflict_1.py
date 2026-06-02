import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.optimize import curve_fit
import time
import os

try:
    from numba import njit

    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

###############################################
# USER SETTINGS
###############################################

filename = "11.csv"

# Physics Parameters
bin_width = 2e-9  # 2 ns binning
max_delay = 80e-9  # ±80 ns window
dead_region_ns = 5  # Remove ±5 ns central crosstalk/dead time artifact

# Aesthetic Settings
PLOT_SMOOTHING_WINDOW = 5  # Used only for visualization, NOT for fitting!


###############################################
# FILE PARSER (Optimized with Pandas)
###############################################

def read_dual_channel_timestamps(filename):
    """
    Reads the 2-channel timestamp CSV at high speed using Pandas.
    Handles comment rows and irregular whitespace optimally.
    """
    print(f"Loading timestamps from {filename}...")
    t0 = time.time()

    # Read the CSV rapidly skipping commented headers, using whitespace/comma delimiters
    df = pd.read_csv(filename, comment='%', header=None, engine='c',
                     sep=r'[,\t ]+', names=["src", "ts"])

    # Filter and extract underlying numpy arrays (sorted guarantee from hardware usually holds, but sorted here to be safe)
    tA = np.sort(df[df['src'] == 1]['ts'].values)
    tB = np.sort(df[df['src'] == 2]['ts'].values)

    print(f"Loaded in {time.time() - t0:.2f}s")
    print(f"  Detector A events: {len(tA):,}")
    print(f"  Detector B events: {len(tB):,}")

    return tA, tB


###############################################
# BUILD CROSS-CORRELATION HISTOGRAM
###############################################

if HAS_NUMBA:
    @njit
    def _compute_histogram_fast(tA, tB, max_delay, bin_width):
        edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
        H = np.zeros(len(edges) - 1, dtype=np.int64)
        j0 = 0
        len_B = len(tB)
        n_bins = len(H)

        for i in range(len(tA)):
            ta_i = tA[i]

            while j0 < len_B and tB[j0] < ta_i - max_delay:
                j0 += 1

            j = j0
            while j < len_B and tB[j] <= ta_i + max_delay:
                dt = tB[j] - ta_i
                idx = int((dt + max_delay) / bin_width)
                if 0 <= idx < n_bins:
                    H[idx] += 1
                j += 1

        centers = 0.5 * (edges[:-1] + edges[1:])
        return centers, H
else:
    def _compute_histogram_fast(tA, tB, max_delay, bin_width):
        print("\n[WARNING] Numba is not installed. Using pure Python fallback.")
        print("For 10 mins of data, this might take a very long time! Run `pip install numba` for 100x speedup.\n")

        edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
        H = np.zeros(len(edges) - 1, dtype=np.int64)
        j0 = 0
        len_B = len(tB)
        n_bins = len(H)

        for i in range(len(tA)):
            ta_i = tA[i]
            while j0 < len_B and tB[j0] < ta_i - max_delay:
                j0 += 1
            j = j0
            while j < len_B and tB[j] <= ta_i + max_delay:
                dt = tB[j] - ta_i
                idx = int((dt + max_delay) / bin_width)
                if 0 <= idx < n_bins:
                    H[idx] += 1
                j += 1
        centers = 0.5 * (edges[:-1] + edges[1:])
        return centers, H


def compute_histogram(tA, tB):
    print("Computing cross-correlation histogram...")
    t0 = time.time()
    centers, H = _compute_histogram_fast(tA, tB, max_delay, bin_width)
    print(f"Histogram computed in {time.time() - t0:.2f}s")
    return centers, H.astype(float)


###############################################
# ANTIBUNCHING MODEL
###############################################

def antibunching_model(tau, g0, tau_c):
    return 1 - (1 - g0) * np.exp(-np.abs(tau) / tau_c)


def fit_model(tau, g2_raw):
    """ Fits the raw valid data avoiding smoothing distortions """
    valid = ~np.isnan(g2_raw)
    try:
        popt, pcov = curve_fit(
            antibunching_model,
            tau[valid],
            g2_raw[valid],
            bounds=([0, 0], [2, 100e-9])  # slightly relaxed boundary
        )
        perr = np.sqrt(np.diag(pcov))
        return popt, perr, valid
    except Exception as e:
        print(f"Fit failed: {e}")
        return [np.nan, np.nan], [np.nan, np.nan], valid


###############################################
# SMOOTHING FILTER (For Display ONLY)
###############################################

def smooth(data, window=5):
    # Fills nans with interpolation just for smoother viz lines
    s = pd.Series(data).interpolate(limit_direction='both')
    kernel = np.ones(window) / window
    return np.convolve(s, kernel, mode='same')


###############################################
# MAIN PIPELINE
###############################################

def main():
    if not os.path.exists(filename):
        print(f"File {filename} not found in this directory.")
        return

    tA, tB = read_dual_channel_timestamps(filename)

    # 1. HBT Histogram
    tau, H = compute_histogram(tA, tB)

    # 2. Experimental Normalization (Mean of outer 25% wings)
    outer_left = H[:len(H) // 4]
    outer_right = H[3 * len(H) // 4:]
    baseline = np.mean(np.concatenate((outer_left, outer_right)))
    g2 = H / baseline

    # 3. Enforce Physical Symmetry
    g2 = 0.5 * (g2 + g2[::-1])

    # 4. Remove artifacts (dead region)
    dead_bins = int(dead_region_ns * 1e-9 / bin_width)
    center = len(g2) // 2
    g2_fit = g2.copy()

    # Notice we define bounds securely.
    start_del = max(0, center - dead_bins)
    end_del = min(len(g2), center + dead_bins + 1)
    g2_fit[start_del:end_del] = np.nan
    g2[start_del:end_del] = np.nan

    # 5. Fit the Antibunching Curve directly to correctly weighted REST data!
    # (Do not fit to smoothed data since smoothing flattens the dip!)
    popt, perr, valid = fit_model(tau, g2_fit)
    g0_fit, tau_fit = popt
    g0_err, tau_err = perr

    print("\n--- FIT RESULTS ---")
    print(f"g²(0) = {g0_fit:.3f} ± {g0_err:.3f}")
    if not np.isnan(tau_fit):
        print(f"Lifetime (τ_c) = {tau_fit * 1e9:.2f} ± {tau_err * 1e9:.2f} ns")

    # 6. Smooth for Visualization
    g2_smooth = smooth(g2, window=PLOT_SMOOTHING_WINDOW)

    # 7. Generate Fit Line & Residuals
    tau_fine = np.linspace(-max_delay, max_delay, 1000)
    g2_fine = antibunching_model(tau_fine, *popt) if not np.isnan(g0_fit) else np.zeros_like(tau_fine)

    # Calculate residuals for the valid points used in the fit
    residuals = np.full_like(g2_fit, np.nan)
    if not np.isnan(g0_fit):
        residuals[valid] = g2_fit[valid] - antibunching_model(tau[valid], *popt)

    ###############################################
    # PUBLICATION PLOT SETUP
    ###############################################

    plt.style.use('default')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'axes.labelsize': 11,
        'axes.titlesize': 13,
        'legend.fontsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })

    fig = plt.figure(figsize=(7, 5.5), dpi=150)
    gs = gridspec.GridSpec(2, 1, height_ratios=[3.5, 1], hspace=0.1)

    # --- TOP PANEL (Main Plot) ---
    ax1 = fig.add_subplot(gs[0])

    # Scatter Raw Data
    ax1.scatter(tau * 1e9, g2, s=8, color='#888888', alpha=0.6, label='Raw Data', zorder=1)

    # Overlay Smoothed Trend
    ax1.plot(tau * 1e9, g2_smooth, color='#1f77b4', linewidth=1.5, alpha=0.9, label='Smoothed Trend', zorder=2)

    # Fit Curve (Red)
    if not np.isnan(g0_fit):
        ax1.plot(tau_fine * 1e9, g2_fine, color='#d62728', linewidth=2, label='Antibunching Fit', zorder=3)

        # Display Fit Text cleanly
        fit_text = (f"$g^{(2)}(0) = {g0_fit:.2f} \\pm {g0_err:.2f}$\n"
                    f"$\\tau_c = {tau_fit * 1e9:.2f} \\pm {tau_err * 1e9:.2f}$ ns")

        # Box properties for text label
        props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
        ax1.text(0.96, 0.05, fit_text, transform=ax1.transAxes, fontsize=11,
                 verticalalignment='bottom', horizontalalignment='right', bbox=props)

    # Guides & Layout
    ax1.axhline(1, linestyle='--', color='black', alpha=0.4, zorder=0)
    ax1.axvline(0, linestyle='--', color='black', alpha=0.4, zorder=0)

    ax1.set_xlim([-max_delay * 1e9, max_delay * 1e9])

    # Adapt Y limits to cut off extreme outliers but show full shape
    y_max = np.nanpercentile(g2, 99) * 1.1 if not np.isnan(np.nanmax(g2)) else 1.5
    y_min = max(0, -0.1)  # allow slight dip below zero safely
    ax1.set_ylim([y_min, max(1.2, y_max)])

    ax1.set_ylabel("$g^{(2)}(\\tau)$")
    ax1.set_title("Second-Order Correlation Function")
    ax1.legend(loc='upper right', framealpha=0.9)
    ax1.grid(alpha=0.25, linestyle=':')

    # Hide top x-axis labels
    plt.setp(ax1.get_xticklabels(), visible=False)

    # --- BOTTOM PANEL (Residuals) ---
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.axhline(0, linestyle='-', color='black', alpha=0.5, linewidth=1)
    ax2.scatter(tau * 1e9, residuals, s=6, color='#d62728', alpha=0.7)

    # Calculate sensible limits for residuals (3 standard deviations)
    if not np.isnan(g0_fit) and np.any(~np.isnan(residuals)):
        res_std = np.nanstd(residuals)
        ax2.set_ylim([-3.5 * res_std, 3.5 * res_std])

    ax2.set_xlabel("Delay Time $\\tau$ (ns)")
    ax2.set_ylabel("Resid.")
    ax2.grid(alpha=0.25, linestyle=':')

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
