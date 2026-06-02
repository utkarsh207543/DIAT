import numpy as np
import matplotlib.pyplot as plt
import re

# ==========================
# USER SETTINGS
# ==========================

filename = "data.csv"

bin_width = 1e-9        # coincidence bin width (seconds)
max_delay = 100e-9      # histogram range ± delay window


# ==========================
# READ MOKU CSV TIMESTAMPS
# ==========================

print("\nReading timestamps from:", filename)

_SPLIT = re.compile(r"[,\t ]+")


def read_moku_csv(fname):

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


tA, tB = read_moku_csv(filename)


# ==========================
# BASIC DETECTOR COUNTS
# ==========================

N1 = len(tA)
N2 = len(tB)

print("\nDetector A counts =", N1)
print("Detector B counts =", N2)


if N1 == 0 or N2 == 0:
    raise RuntimeError("One detector has zero counts")


# ==========================
# MEASUREMENT TIME
# ==========================

T_start = min(tA[0], tB[0])
T_stop = max(tA[-1], tB[-1])

T = T_stop - T_start

print("Integration time T =", T, "seconds")


# ==========================
# COUNT RATES
# ==========================

R1 = N1 / T
R2 = N2 / T

print("\nDetector A rate =", R1, "counts/sec")
print("Detector B rate =", R2, "counts/sec")


# ==========================
# BUILD COINCIDENCE HISTOGRAM
# ==========================

print("\nComputing coincidence histogram...")

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

        index = int((dt + max_delay) / bin_width)

        if 0 <= index < len(H):
            H[index] += 1

        j += 1


# ==========================
# FIND CENTER BIN COINCIDENCES
# ==========================

center_index = len(H) // 2

C12 = H[center_index]

print("\nCenter-bin coincidence counts C12 =", int(C12))


# ==========================
# COMPUTE g2(0)
# ==========================

delta_t = bin_width

g2_0 = (C12 * T) / (N1 * N2 * delta_t)

print("\n==============================")
print("RESULTS")
print("==============================")

print("N1 =", N1)
print("N2 =", N2)
print("C12 =", int(C12))
print("Δt =", delta_t)
print("T =", T)

print("\ng²(0) =", g2_0)


# ==========================
# HISTOGRAM NORMALIZATION METHOD
# ==========================

side_bins = np.concatenate((H[:len(H)//4], H[3*len(H)//4:]))

baseline = np.mean(side_bins)

g2_histogram_method = C12 / baseline

print("\ng²(0) from histogram method =", g2_histogram_method)


# ==========================
# INTERPRET RESULT
# ==========================

print("\nINTERPRETATION:")

if g2_0 > 1.5:
    print("Thermal light (LED-like bunching)")

elif 0.8 < g2_0 < 1.2:
    print("Coherent light (laser-like statistics)")

elif g2_0 < 0.5:
    print("Possible single-photon antibunching")

else:
    print("Intermediate / mixed statistics")


# ==========================
# PLOT HISTOGRAM
# ==========================

plt.figure(figsize=(7,5))

plt.bar(tau * 1e9, H, width=1, color="deeppink")

plt.xlabel("Delay (ns)")
plt.ylabel("Coincidence counts")

plt.title("Coincidence Histogram")

plt.tight_layout()

plt.show()