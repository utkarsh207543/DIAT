import numpy as np
import matplotlib.pyplot as plt
import re
import sys

# Target file
filename = sys.argv[1] if len(sys.argv) > 1 else "11.csv"

# Restrict the analysis entirely to the ±10 ns window
bin_width = 1e-9          # 1 ns bins
max_delay = 10e-9         # EXACTLY 10ns window

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

print(f"Loading timestamps for {filename}...")
tA, tB = read_dual_channel_timestamps(filename)
print(f"Detector A events: {len(tA)}")
print(f"Detector B events: {len(tB)}")

# Compute histogram restricted to +- 10ns
print("\nScanning for coincidences in the +/- 10 ns window...")
tau, H = compute_histogram(tA, tB)

# Calculate total coincidences precisely in this window
total_coincidences = int(np.sum(H))
print(f"=====================================")
print(f"Total RAW coincidences (+/- 10ns): {total_coincidences}")
print(f"=====================================")

# Plot RAW coincidences as a bar chart
plt.figure(figsize=(8, 5))
plt.bar(tau*1e9, H, width=0.9, color='#0055FF', alpha=0.9, edgecolor='black')
plt.axvline(0, color='red', linestyle='--', linewidth=2, alpha=0.8)

plt.xlabel("Delay (ns)", fontweight='bold', fontsize=12)
plt.ylabel("Raw Coincidences (Count)", fontweight='bold', fontsize=12)
plt.title(f"Focus: ±10 ns Coincidence Window for {filename}\nTotal Photons Matched: {total_coincidences}", fontweight='bold')

plt.xlim([-11, 11])
plt.xticks(np.arange(-10, 11, 2))

plt.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()

out_filename = "lol2_plot.png"
plt.savefig(out_filename, dpi=300)
print(f"\nSaved visualization to: {out_filename}")

plt.show()
