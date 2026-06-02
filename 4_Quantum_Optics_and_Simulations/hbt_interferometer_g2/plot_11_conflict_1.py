import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import re

# =============================
# PARAMETERS
# =============================

filename = "A1.csv"
bin_width = 1e-9
max_delay = 800e-9
dead_zone = 50e-9   # exclude ±5 ns around zero from baseline estimation

print("\n--- Processing Real HBT Data ---")
print(f"Reading timestamps from {filename}...")

# =============================
# READ TIMESTAMPS
# =============================

_SPLIT = re.compile(r"[,\t ]+")

def read_dual_channel_timestamps(fname):
    ch1, ch2 = [], []

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

if len(tA) == 0 or len(tB) == 0:
    raise RuntimeError("One detector has zero events.")


# =============================
# CROSS-CORRELATION
# =============================

print("Running cross-correlation...")

edges = np.arange(-max_delay, max_delay + bin_width, bin_width)

tau = 0.5 * (edges[:-1] + edges[1:])

H = np.zeros(len(tau))

j0 = 0

for ta in tA:

    while j0 < len(tB) and tB[j0] < ta - max_delay:
        j0 += 1

    j = j0

    while j < len(tB) and tB[j] <= ta + max_delay:

        dt = tB[j] - ta

        idx = int((dt + max_delay) / bin_width)

        if 0 <= idx < len(H):
            H[idx] += 1

        j += 1


# =============================
# SAFE BASELINE NORMALIZATION
# =============================

baseline_region = np.logical_and(
    np.abs(tau) > dead_zone,
    np.abs(tau) > 0.6 * max_delay
)

baseline_vals = H[baseline_region]

if len(baseline_vals) == 0:
    raise RuntimeError("Baseline region empty")

baseline = np.mean(baseline_vals)

if baseline <= 0:
    print("WARNING: baseline too small — using fallback normalization")
    baseline = np.max(H)

g2 = H / baseline


# =============================
# CLEAN INVALID VALUES
# =============================

valid = np.isfinite(g2)

tau_valid = tau[valid]
g2_valid = g2[valid]


# =============================
# ENFORCE SYMMETRY
# =============================

g2_valid = 0.5 * (g2_valid + g2_valid[::-1])


# =============================
# ANTIBUNCHING MODEL
# =============================

def antibunching_model(t, g0, tc):

    return 1 - (1 - g0) * np.exp(-np.abs(t) / tc)


# =============================
# CURVE FIT
# =============================

try:

    popt, _ = curve_fit(
        antibunching_model,
        tau_valid,
        g2_valid,
        p0=[0.5, 10e-9],
        bounds=([0, 1e-12], [1.5, 1e-6])
    )

    g0_fit, tc_fit = popt

    print(f"\nEstimated g²(0) = {g0_fit:.3f}")
    print(f"Emitter lifetime τ = {tc_fit*1e9:.2f} ns")

    fit_success = True

except:

    print("Fit failed — insufficient coincidence statistics")
    fit_success = False


# =============================
# PLOT
# =============================

plt.figure(figsize=(7,5))

plt.scatter(
    tau_valid * 1e9,
    g2_valid,
    color='#ff007f',
    s=60,
    alpha=0.9,
    label="Real Moku Data"
)

if fit_success:

    tau_fit = np.linspace(-max_delay, max_delay, 500)

    plt.plot(
        tau_fit * 1e9,
        antibunching_model(tau_fit, *popt),
        'black',
        linewidth=2.5,
        label="Fit"
    )

plt.axhline(1.0, linestyle='--', linewidth=2, alpha=0.5)

plt.xlim([-40,40])

plt.xlabel("Delay Time (ns)", fontweight='bold')

plt.ylabel("g²(τ)", fontweight='bold')

plt.title(f"HBT Analysis: {filename}", fontweight='bold')

if fit_success:

    stats_str = f"g²(0) = {g0_fit:.2f}\nτc = {tc_fit*1e9:.1f} ns"

    plt.text(
        0.5,
        0.1,
        stats_str,
        transform=plt.gca().transAxes,
        fontsize=14,
        fontweight='bold',
        ha='center'
    )

plt.legend()

plt.tight_layout()

plt.savefig("real_hbt_plot.png", dpi=300)

plt.show()