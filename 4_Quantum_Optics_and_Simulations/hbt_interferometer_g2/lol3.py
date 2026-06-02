import numpy as np
import matplotlib.pyplot as plt
import re
import sys

# Target file
filename = sys.argv[1] if len(sys.argv) > 1 else "11.csv"

# We will scan out to 20ns window (radius 10ns)
max_delay = 15e-9 

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

print(f"Loading {filename}...")
tA, tB = read_dual_channel_timestamps(filename)
print(f"Detector A events: {len(tA)}")
print(f"Detector B events: {len(tB)}")

print("Extrapolating explicit temporal offsets without binning...")

# Extract precise, unbinned time differences between photons
deltas = []
j0 = 0
for i in range(len(tA)):
    ta = tA[i]
    while j0 < len(tB) and tB[j0] < ta - max_delay:
        j0 += 1
    j = j0
    while j < len(tB) and tB[j] <= ta + max_delay:
        deltas.append(tB[j] - ta)
        j += 1

deltas = np.array(deltas)

# Calculate coincidences for each window size exactly
window_sizes = np.arange(1, 21) # 1 to 20 ns
coincidence_sums = []

print("\n--- Coincidences vs. Window Size ---")
for w in window_sizes:
    radius = (w * 1e-9) / 2.0
    # Count precisely how many events fall strictly within +/- radius
    count = int(np.sum((deltas >= -radius) & (deltas <= radius)))
    coincidence_sums.append(count)
    print(f"Window: {w:2d} ns ([-{w/2.0:4.1f}, +{w/2.0:4.1f}] ns) -> {count} coincidences")

# Plot the progression
plt.figure(figsize=(8, 5))
plt.plot(window_sizes, coincidence_sums, marker='o', markerfacecolor='white', markersize=8, markeredgewidth=2, 
         linestyle='-', color='#800080', linewidth=2.5)

plt.xlabel("Coincidence Window Size (ns)", fontweight='bold', fontsize=12)
plt.ylabel("Cumulative Coincidences", fontweight='bold', fontsize=12)

title_text = f"Coincidences Caught vs Window Size [1 to 20 ns]\n{filename}"
plt.title(title_text, fontweight='bold')

plt.xlim([0, 21])
plt.xticks(np.arange(0, 21, 2))
plt.ylim([0, max(coincidence_sums) * 1.15 if coincidence_sums else 1])

plt.grid(axis='both', alpha=0.3, linestyle='--')
plt.tight_layout()

out_filename = "lol3_plot.png"
plt.savefig(out_filename, dpi=300)
print(f"\nPlot saved to: {out_filename}")

plt.show()
