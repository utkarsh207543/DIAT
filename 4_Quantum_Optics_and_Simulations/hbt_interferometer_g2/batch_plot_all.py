import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re
import glob

bin_width = 1e-9
max_delay = 100e-9

_SPLIT = re.compile(r"[,\t ]+")

def read_dual_channel_timestamps(fname):
    ch1, ch2 = [], []
    with open(fname, "r", encoding="utf-8", errors="ignore") as f:
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

def antibunching_model(t, g0, tc):
    return 1 - (1 - g0) * np.exp(-np.abs(t) / tc)

def process_file_simstyle(filename):
    print(f"Loading {filename}...")
    tA, tB = read_dual_channel_timestamps(filename)
    if len(tA) < 10 or len(tB) < 10:
        return "Insufficient events"

    edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
    tau = 0.5 * (edges[:-1] + edges[1:])
    H = np.zeros(len(tau))

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

    outer_left = H[:len(H)//4]
    outer_right = H[3*len(H)//4:]
    baseline = np.mean(np.concatenate((outer_left, outer_right)))
    
    max_c = np.max(H)
    has_stats = (max_c >= 20 and baseline >= 1.5)

    g2 = H / baseline if baseline > 0 else H
    g2 = 0.5 * (g2 + g2[::-1])

    fit_success = False
    g0_fit, tc_fit = 1.0, 0.0
    if has_stats:
        try:
            popt, _ = curve_fit(antibunching_model, tau, g2, p0=[0.2, 10e-9], bounds=([0, 1e-12], [np.inf, np.inf]))
            g0_fit, tc_fit = popt
            fit_success = True
        except:
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

    ax.scatter(tau*1e9, g2, color='#ff007f', s=60, alpha=0.9, label="Real Moku Data", zorder=3)
    
    if fit_success:
        tau_fit_axis = np.linspace(-max_delay, max_delay, 500)
        ax.plot(tau_fit_axis*1e9, antibunching_model(tau_fit_axis, *popt), 'black', linewidth=2.5, label="Fit", zorder=4)

    ax.axhline(1.0, color='gray', linestyle='--', linewidth=2, alpha=0.5, zorder=1)

    ax.set_xlim([-40, 40])
    
    if fit_success:
        max_y = max(1.25, np.max(g2) * 1.1)
        ax.set_ylim([0, max_y])
        stats_str = f"g²(0) = {g0_fit:.2f}\n$\\tau_c$ = {tc_fit*1e9:.1f} ns"
        ax.text(0.5, 0.1, stats_str, transform=ax.transAxes, 
                fontsize=14, fontweight='bold', va='bottom', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', alpha=0.9))
    else:
        max_y = max(2.05, np.max(g2) * 1.1) if len(g2) > 0 else 2.05
        if np.isnan(max_y) or max_y < 1.25: max_y = 1.25
        ax.set_ylim([0, max_y])
        stats_str = f"LOW STATS\n(Max: {int(max_c)} hits)"
        ax.text(0.5, 0.1, stats_str, transform=ax.transAxes, 
                fontsize=14, fontweight='bold', va='bottom', ha='center', color='black',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='red', linewidth=2, alpha=0.9))

    ax.set_xlabel("Delay Time (ns)", fontweight='bold')
    ax.set_ylabel("g²(τ)", fontweight='bold')
    ax.set_title(f"HBT Analysis: {filename}", fontweight='bold')

    ax.legend(loc='lower right', frameon=False)
    plt.tight_layout()

    out_file = filename.replace('.csv', '_simstyle.png')
    plt.savefig(out_file, dpi=300)
    plt.close()

    if not has_stats:
        return f"REJECTED - Low Stats (Max {int(max_c)})"
    return f"VALID - g²(0) ≈ {g0_fit:.3f}"

def main():
    files = sorted(glob.glob("*.csv"), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
    print("Starting batch processing using pure Simulation aesthetic...")
    for f in files:
        if "-series" in f: continue
        res = process_file_simstyle(f)
        print(f"Processed {f} : {res}")

if __name__ == '__main__':
    main()
