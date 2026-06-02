import numpy as np
import matplotlib.pyplot as plt
import re
import sys

filename = sys.argv[1] if len(sys.argv) > 1 else "xx.csv"
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

print(f"Loading {filename}...")
tA, tB = read_dual_channel_timestamps(filename)

edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
tau = 0.5 * (edges[:-1] + edges[1:])
H = np.zeros(len(tau))

print("Computing full histogram to secure normalization baseline...")
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

# Normalize exactly like a standard g2
g2 = H / baseline if baseline > 0 else H
# Apply symmetry folding
g2 = 0.5 * (g2 + g2[::-1])

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

# Plot identical to a standard g2 curve, but ultra-zoomed
ax.scatter(tau*1e9, g2, color='#0000FF', s=100, alpha=1.0, label="Raw g² points", zorder=3)
ax.plot(tau*1e9, g2, color='#0000FF', linewidth=2.0, alpha=0.4, zorder=2) # Faint connecting line

# Force the exact [-10, 10] physical view window
ax.set_xlim([-10.5, 10.5])
ax.set_xticks(np.arange(-10, 11, 2))

# Use standard g2 Y-axis bounds
ax.set_ylim([0.0, 2.05])
ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])

# Highlight the 1.0 baseline
ax.axhline(1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.5, zorder=1)

ax.set_xlabel("Delay Time (ns)", fontweight='bold')
ax.set_ylabel("g²(τ)", fontweight='bold')
ax.set_title(f"g² Zoom: -10 ns to +10 ns ({filename})", fontweight='bold')

plt.tight_layout()
out_filename = "lol4_plot.png"
plt.savefig(out_filename, dpi=300)
print(f"\nCreated requested g2 plot at: {out_filename}")

plt.show()
