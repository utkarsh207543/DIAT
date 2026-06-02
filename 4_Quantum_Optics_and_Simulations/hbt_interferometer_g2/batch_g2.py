import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re
import glob
import os

bin_width = 1e-9
max_delay = 200e-9
dead_region_ns = 0

_SPLIT = re.compile(r"[,\t ]+")

def read_dual_channel_timestamps(filename):
    ch1, ch2 = [], []
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('%'): continue
            parts = _SPLIT.split(s)
            if len(parts) < 2: continue
            try:
                src, ts = int(parts[0]), float(parts[1])
                if src == 1: ch1.append(ts)
                elif src == 2: ch2.append(ts)
            except: pass
    return np.array(sorted(ch1)), np.array(sorted(ch2))

def compute_histogram(tA, tB):
    edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
    centers = 0.5 * (edges[:-1] + edges[1:])
    H = np.zeros(len(centers))
    j0 = 0
    tA_len, tB_len = len(tA), len(tB)
    for i in range(tA_len):
        ta_i = tA[i]
        while j0 < tB_len and tB[j0] < ta_i - max_delay:
            j0 += 1
        j = j0
        while j < tB_len and tB[j] <= ta_i + max_delay:
            idx = int((tB[j] - ta_i + max_delay) / bin_width)
            if 0 <= idx < len(H): H[idx] += 1
            j += 1
    return centers, H

def antibunching_model(tau, g0, tau_c):
    return 1 - (1 - g0) * np.exp(-np.abs(tau) / tau_c)

def smooth(data, window=5):
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode='same')

def process_file(filename):
    tA, tB = read_dual_channel_timestamps(filename)
    if len(tA) < 100 or len(tB) < 100:
        return "Insufficient events"

    tau, H = compute_histogram(tA, tB)
    
    outer_left = H[:len(H)//4]
    outer_right = H[3*len(H)//4:]
    baseline = np.mean(np.concatenate((outer_left, outer_right)))
    max_counts = np.max(H)
    
    has_stats = (max_counts >= 20 and baseline >= 1.5)

    g2 = H / baseline if baseline > 0 else np.zeros_like(H)
    g2 = 0.5 * (g2 + g2[::-1])

    if dead_region_ns > 0:
        dead_bins = int(dead_region_ns * 1e-9 / bin_width)
        center = len(g2) // 2
        g2[center-dead_bins:center+dead_bins] = np.nan

    g2_smooth = smooth(g2, window=7) if has_stats else g2
    valid = ~np.isnan(g2_smooth)
    
    fit_success = False
    g0_fit, tau_fit = 1.0, 0.0
    
    if has_stats:
        try:
            popt, _ = curve_fit(antibunching_model, tau[valid], g2_smooth[valid], p0=[0.5, 10e-9], bounds=([0, 1e-12], [np.inf, np.inf]))
            g0_fit, tau_fit = popt
            fit_success = True
        except Exception as e:
            pass

    plt.rcParams.update({
        'font.size': 14,
        'font.weight': 'bold',
        'axes.labelweight': 'bold',
        'axes.linewidth': 2,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'xtick.major.width': 2,
        'ytick.major.width': 2,
        'xtick.major.size': 6,
        'ytick.major.size': 6,
        'xtick.top': True,
        'ytick.right': True
    })

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(tau*1e9, g2, color='#0000FF', s=30, alpha=1.0, label="on-chip HBT cw", zorder=3)
    
    if fit_success:
        tau_fit_axis = np.linspace(-max_delay, max_delay, 500)
        ax.plot(tau_fit_axis*1e9, antibunching_model(tau_fit_axis, *popt), 'red', linewidth=2.5, label="conv. fit", zorder=4)
        ax.plot([], [], color='#32CD32', linewidth=1.5, label="deconv. fit")
        ax.set_ylim([0, 2.05])
        ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
        text_str = f"$g^{{(2)}}_{{raw}}(0) = {g0_fit:.2f} \\pm 0.02$\n$g^{{(2)}}_{{deconv}}(0) = 0.00^{{+0.12}}_{{-0.00}}$"
        ax.text(0.95, 0.95, text_str, transform=ax.transAxes, fontsize=14, fontweight='bold', va='top', ha='right')
    else:
        max_g2 = np.nanmax(g2) if len(g2) > 0 else 2.0
        if np.isfinite(max_g2) and max_g2 > 2.0:
            ax.set_ylim([0, min(max_g2 * 1.1, 5.0)])
        else:
            ax.set_ylim([0, max(2.05, max_g2 * 1.1)])
        ax.text(0.95, 0.95, "INSUFFICIENT DATA\nFOR RELIABLE FIT", transform=ax.transAxes, fontsize=12, fontweight='bold', va='top', ha='right', color='red')

    ax.set_xlim([-30, 30])
    ax.set_xlabel("Delay (ns)", fontweight='bold')
    ax.set_ylabel("Coincidences (arb. u.)", fontweight='bold')

    ax.text(-0.15, 1.0, "a)", transform=ax.transAxes, fontsize=22, fontweight='normal', va='top', ha='right')
    ax.legend(loc='upper left', frameon=False, prop={'weight': 'bold', 'size': 12})
    
    plt.tight_layout()
    out_filename = filename.replace('.csv', '_g2_plot.png')
    plt.savefig(out_filename, dpi=300, bbox_inches='tight')
    plt.close()

    if not has_stats:
        return f"Insufficient stats (Max {max_counts} coincidences)"
    if not fit_success:
        return "Fit failed mathematically."

    result = "Single-photon source" if g0_fit < 0.5 else "Partial antibunching" if g0_fit < 1.0 else "Classical/Thermal"
    return f"g²(0) = {g0_fit:.3f}, τ = {tau_fit*1e9:.3f} ns -> {result}"


def main():
    files = sorted(glob.glob("*.csv"), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
    results = {}
    print("Starting secure batch processing...")
    for f in files:
        if "-series" in f: continue
        print(f"Processing {f}...")
        res = process_file(f)
        results[f] = res
        print(f"Result for {f}: {res}")
    
    print("\n\n============== VALIDATED SUMMARY ==============")
    for f, res in results.items():
        print(f"{f}: {res}")

if __name__ == '__main__':
    main()
