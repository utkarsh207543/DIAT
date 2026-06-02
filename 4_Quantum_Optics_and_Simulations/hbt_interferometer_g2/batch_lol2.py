import numpy as np
import matplotlib.pyplot as plt
import re
import glob
import os

# Confining analysis window
bin_width = 1e-9
max_delay = 10e-9

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

def process_file(filename):
    print(f"Loading timestamps for {filename}...")
    tA, tB = read_dual_channel_timestamps(filename)
    if len(tA) < 10 or len(tB) < 10:
        return "Insufficient events"

    # Compute strictly within +- 10ns
    tau, H = compute_histogram(tA, tB)
    total_coincidences = int(np.sum(H))
    
    plt.figure(figsize=(8, 5))
    plt.bar(tau*1e9, H, width=0.9, color='#0055FF', alpha=0.9, edgecolor='black')
    plt.axvline(0, color='red', linestyle='--', linewidth=2, alpha=0.8)

    plt.xlabel("Delay (ns)", fontweight='bold', fontsize=12)
    plt.ylabel("Raw Coincidences (Count)", fontweight='bold', fontsize=12)
    plt.title(f"Focus: ±10 ns Coincidence Window for {filename}\nTotal Photons Matched: {total_coincidences}", fontweight='bold')

    plt.xlim([-11, 11])
    plt.xticks(np.arange(-10, 11, 2))

    max_val = np.max(H)
    if max_val > 0:
        plt.ylim([0, max_val * 1.15])
    else:
        plt.ylim([0, 5]) # Keep minimum scaling so completely empty plots aren't crushed

    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()

    out_filename = filename.replace('.csv', '_lol2_plot.png')
    plt.savefig(out_filename, dpi=300)
    plt.close()
    
    return f"Total Coincidences: {total_coincidences}"

def main():
    files = sorted(glob.glob("*.csv"), key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)
    results = {}
    print("Starting batch lol2 processing (±10ns window)...")
    for f in files:
        if "-series" in f: continue
        res = process_file(f)
        results[f] = res
        print(f"Result for {f}: {res}\n")
    
    print("\n============== LOL2 SUMMARY (±10ns) ==============")
    for f, res in results.items():
        print(f"{f}: {res}")

if __name__ == '__main__':
    main()
