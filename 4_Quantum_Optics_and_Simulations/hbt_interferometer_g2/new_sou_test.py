import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re
from collections import defaultdict

# ================= PARAMETERS =================
filename = "xx.csv"

bin_width = 1e-9
max_delay = 100e-9

print("\n--- Processing Multi-Channel Timestamp Data ---")
print(f"Reading timestamps from {filename}...")

# ================= UNIVERSAL PARSER =================
_SPLIT = re.compile(r"[,\t ]+")

def read_all_channels(fname):
    channels = defaultdict(list)

    with open(fname, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:

            line = line.strip()

            # skip header
            if not line or line.lower().startswith("channel"):
                continue

            parts = _SPLIT.split(line)

            try:
                ch = int(parts[0])
                ts = float(parts[1]) * 1e-9  # convert ns → seconds
                channels[ch].append(ts)

            except:
                pass

    for ch in channels:
        channels[ch] = np.array(sorted(channels[ch]))

    return channels


channels = read_all_channels(filename)


# ================= BASIC CHANNEL STATISTICS =================
print("\n--- Channel Statistics ---")

for ch in sorted(channels.keys()):
    print(f"Channel {ch}: {len(channels[ch])} events")


# ================= EVENT RATE HISTOGRAM =================
plt.figure(figsize=(7,5))

for ch in sorted(channels.keys()):
    plt.hist(
        channels[ch]*1e9,
        bins=200,
        alpha=0.5,
        label=f"Ch {ch}"
    )

plt.xlabel("Timestamp (ns)")
plt.ylabel("Counts")
plt.title("Event Distribution per Channel")
plt.legend()
plt.tight_layout()
plt.show()


# ================= SELECT PAIR FOR HBT =================
# choose detectors here

detA = 1
detB = 2

tA = channels[detA]
tB = channels[detB]

print(f"\nRunning HBT between Channel {detA} and {detB}")


# ================= CROSS-CORRELATION =================
edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
tau = 0.5 * (edges[:-1] + edges[1:])
H = np.zeros(len(tau))


j0 = 0
tB_len = len(tB)

for ta in tA:

    while j0 < tB_len and tB[j0] < ta - max_delay:
        j0 += 1

    j = j0

    while j < tB_len and tB[j] <= ta + max_delay:

        idx = int((tB[j] - ta + max_delay) / bin_width)

        if 0 <= idx < len(H):
            H[idx] += 1

        j += 1


# ================= NORMALIZATION =================
outer_left = H[:len(H)//4]
outer_right = H[3*len(H)//4:]

baseline = np.mean(np.concatenate((outer_left, outer_right)))

g2 = H / baseline
g2 = 0.5 * (g2 + g2[::-1])


# ================= FIT MODEL =================
def antibunching_model(t, g0, tc):
    return 1 - (1 - g0) * np.exp(-np.abs(t)/tc)


popt, _ = curve_fit(
    antibunching_model,
    tau,
    g2,
    p0=[0.3, 10e-9],
    bounds=([0,1e-12],[2,np.inf])
)

g0_fit, tc_fit = popt


print(f"\nExtracted g²(0) = {g0_fit:.3f}")
print(f"Lifetime τ = {tc_fit*1e9:.2f} ns")


# ================= FINAL PLOT =================
plt.figure(figsize=(7,5))

plt.scatter(
    tau*1e9,
    g2,
    s=40,
    label="Measured g²(τ)"
)

fit_axis = np.linspace(-max_delay, max_delay, 500)

plt.plot(
    fit_axis*1e9,
    antibunching_model(fit_axis,*popt),
    linewidth=2,
    label="Fit"
)

plt.axhline(1,color='gray',linestyle='--')

plt.xlabel("Delay Time (ns)")
plt.ylabel("g²(τ)")
plt.title(f"HBT: Ch{detA} vs Ch{detB}")

plt.legend()
plt.tight_layout()
plt.show()