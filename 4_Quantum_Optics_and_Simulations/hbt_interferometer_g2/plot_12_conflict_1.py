import numpy as np

# =========================
# USER SETTINGS
# =========================
filename = "cleaned_timestamps.csv"   # change to your file
dt = 1e-9               # coincidence window (1 ns typical)

# =========================
# LOAD DATA (FIXED)
# =========================
data = np.loadtxt(filename, comments='%', delimiter=',')

channel = data[:, 0]
timestamps = data[:, 1]

# =========================
# SPLIT CHANNELS
# =========================
ch1 = timestamps[channel == 1]
ch2 = timestamps[channel == 2]

print("Detector counts:")
print("N1 =", len(ch1))
print("N2 =", len(ch2))

# =========================
# FIND COINCIDENCES
# =========================
i = 0
j = 0
C12 = 0

while i < len(ch1) and j < len(ch2):

    diff = ch1[i] - ch2[j]

    if abs(diff) <= dt:
        C12 += 1
        i += 1
        j += 1

    elif diff < 0:
        i += 1
    else:
        j += 1

print("Coincidences =", C12)

# =========================
# ACQUISITION TIME
# =========================
T = timestamps.max() - timestamps.min()

# =========================
# COMPUTE g2(0)
# =========================
N1 = len(ch1)
N2 = len(ch2)

g2 = (C12 * T) / (N1 * N2 * dt)

print("\nResults:")
print("Acquisition time =", T, "seconds")
print("g2(0) =", g2)