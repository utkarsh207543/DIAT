import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re

# ===============================
# 1. USER PARAMETERS
# ===============================

filename = "xx.csv"

bin_width = 1e-9        # 1 ns bins
max_delay = 500e-9      # ±500 ns coincidence window

print("\n--- Processing Real HBT Data ---")
print(f"Reading timestamps from {filename}...")


# ===============================
# 2. MOKU CSV PARSER
# ===============================

_SPLIT = re.compile(r"[,\t ]+")

def read_dual_channel_timestamps(fname):

    ch1 = []
    ch2 = []

    with open(fname, "r", encoding="utf-8", errors="ignore") as f:
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

                if src == 1:
                    ch1.append(ts)

                elif src == 2:
                    ch2.append(ts)

            except:
                pass

    return np.array(sorted(ch1)), np.array(sorted(ch2))


tA, tB = read_dual_channel_timestamps(filename)

print(f"Detector A captured: {len(tA)} events")
print(f"Detector B captured: {len(tB)} events")


# ===============================
# 3. AUTO-DETECT TIMESTAMP UNITS
# ===============================

print("\nChecking timestamp units...")

median_spacing = np.median(np.diff(tA))

if median_spacing > 1e-3:
    print("Detected timestamps likely in nanoseconds → converting to seconds")
    tA *= 1e-9
    tB *= 1e-9

elif median_spacing > 1:
    print("Detected timestamps likely in picoseconds → converting to seconds")
    tA *= 1e-12
    tB *= 1e-12

else:
    print("Timestamps already in seconds ✔")


print("Timestamp range A:", tA.min(), "to", tA.max())
print("Timestamp range B:", tB.min(), "to", tB.max())


# ===============================
# 4. CROSS-CORRELATION ENGINE
# ===============================

print("\nRunning coincidence cross-correlation...")

edges = np.arange(-max_delay, max_delay + bin_width, bin_width)

tau = 0.5 * (edges[:-1] + edges[1:])

H = np.zeros(len(tau))


j0 = 0
tA_len = len(tA)
tB_len = len(tB)

for i in range(tA_len):

    ta = tA[i]

    while j0 < tB_len and tB[j0] < ta - max_delay:
        j0 += 1

    j = j0

    while j < tB_len and tB[j] <= ta + max_delay:

        idx = int((tB[j] - ta + max_delay) / bin_width)

        if 0 <= idx < len(H):
            H[idx] += 1

        j += 1


# ===============================
# 5. SAFE NORMALIZATION
# ===============================

print("\nNormalizing coincidence histogram...")

outer_left = H[:len(H)//4]
outer_right = H[3*len(H)//4:]

baseline_region = np.concatenate((outer_left, outer_right))

baseline_region = baseline_region[baseline_region > 0]

if len(baseline_region) == 0:

    raise ValueError(
        "\nERROR: No coincidence counts in baseline region.\n"
        "Possible reasons:\n"
        "1) Wrong timestamp units\n"
        "2) Too small coincidence window\n"
        "3) No photon correlations present\n"
        "Try increasing max_delay."
    )

baseline = np.mean(baseline_region)

print("Baseline coincidence level =", baseline)


g2 = H / baseline


# symmetry enforcement

g2 = 0.5 * (g2 + g2[::-1])


# ===============================
# 6. ANTIBUNCHING MODEL FIT
# ===============================

def antibunching_model(t, g0, tc):

    return 1 - (1 - g0) * np.exp(-np.abs(t) / tc)


print("\nPerforming curve fitting...")

popt, _ = curve_fit(
    antibunching_model,
    tau,
    g2,
    p0=[0.3, 10e-9],
    bounds=([0, 1e-12], [1.5, 1e-6])
)

g0_fit, tc_fit = popt


print("\n==============================")
print(f"Estimated g²(0) = {g0_fit:.3f}")
print(f"Emitter lifetime τ = {tc_fit*1e9:.2f} ns")
print("==============================\n")


# ===============================
# 7. PUBLICATION-QUALITY PLOT
# ===============================

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


fig, ax = plt.subplots(figsize=(7,5))


ax.scatter(
    tau * 1e9,
    g2,
    color='#ff007f',
    s=60,
    alpha=0.9,
    label="Measured Data",
    zorder=3
)


tau_fit_axis = np.linspace(-max_delay, max_delay, 500)

ax.plot(
    tau_fit_axis * 1e9,
    antibunching_model(tau_fit_axis, *popt),
    'black',
    linewidth=2.5,
    label="Fit",
    zorder=4
)


ax.axhline(1.0, linestyle='--', linewidth=2, alpha=0.5)


ax.set_xlim([-50, 50])


max_y = max(1.25, np.max(g2) * 1.1)

ax.set_ylim([0, max_y])


ax.set_xlabel("Delay Time (ns)")
ax.set_ylabel("g²(τ)")
ax.set_title(f"HBT Analysis: {filename}")


stats_text = (
    f"g²(0) = {g0_fit:.2f}\n"
    f"τ = {tc_fit*1e9:.1f} ns"
)


ax.text(
    0.5,
    0.1,
    stats_text,
    transform=ax.transAxes,
    fontsize=14,
    va='bottom',
    ha='center',
    bbox=dict(
        boxstyle='round',
        facecolor='white',
        edgecolor='black'
    )
)


ax.legend(frameon=False)


plt.tight_layout()


output_file = "real_hbt_plot.png"

plt.savefig(output_file, dpi=300)


print("Saved plot to:", output_file)


plt.show()