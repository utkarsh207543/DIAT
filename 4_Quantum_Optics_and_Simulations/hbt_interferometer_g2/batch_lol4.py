import numpy as np
import matplotlib.pyplot as plt
import re
import glob
import os

bin_width = 1e-9
max_delay = 200e-9

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

def process_file_lol4(filename):
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
    
    # Calculate crude g2(0) inside central bin just for rough reporting
    center_idx = len(g2) // 2
    g2_0_val = np.mean(g2[center_idx-1:center_idx+2]) if has_stats else np.nan

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
    ax.scatter(tau*1e9, g2, color='#0000FF', s=100, alpha=1.0, label="Raw g² points", zorder=3)
    ax.plot(tau*1e9, g2, color='#0000FF', linewidth=2.0, alpha=0.4, zorder=2)

    ax.set_xlim([-10.5, 10.5])
    ax.set_xticks(np.arange(-10, 11, 2))
    ax.set_ylim([0.0, 2.05])
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])

    ax.axhline(1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.5, zorder=1)

    ax.set_xlabel("Delay Time (ns)", fontweight='bold')
    ax.set_ylabel("g²(τ)", fontweight='bold')
    
    title_mod = "" if has_stats else " [LOW STATS ARTIFACT]"
    ax.set_title(f"Focus: -10 to +10 ns ({filename}){title_mod}", fontweight='bold', color='black' if has_stats else 'red')
    
    if not has_stats:
        ax.text(0.5, 0.9, f"Max absolute raw coincidences: {int(max_c)}", transform=ax.transAxes, 
                ha='center', va='top', color='red', fontweight='bold', fontsize=12)

    plt.tight_layout()
    out_filename = filename.replace('.csv', '_lol4_plot.png')
    plt.savefig(out_filename, dpi=300)
    plt.close()
    
    if not has_stats:
        return f"REJECTED - Low Stats (Max {int(max_c)} hits)"
    return f"VALID - g²(0) ≈ {g2_0_val:.3f}"

def main():
    files = sorted(glob.glob("*.csv"), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
    results = {}
    print("Starting batch lol4 processing [-10 to +10 ns zoom]...")
    for f in files:
        if "-series" in f: continue
        res = process_file_lol4(f)
        results[f] = res
        print(f"Processed {f} : {res}")
    
    print("\n============== ZOOMED g2(0) VALIDATION ==============")
    for f, res in results.items():
        print(f"{f}: {res}")

if __name__ == '__main__':
    main()
