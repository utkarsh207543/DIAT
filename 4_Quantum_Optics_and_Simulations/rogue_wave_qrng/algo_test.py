import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import os

# -------------------------------
# PATH SETUP
# -------------------------------
BASE_DIR = os.getcwd()          # rw/
DATA_DIR = os.path.join(BASE_DIR, "data")

bandwidths = np.arange(15, 1, -1)   # {15, 14, ..., 2}
rogue_threshold = 2.0               # use 2.2 if desired

Pmax = []
SWH = []
TimesFactor = []
valid_B = []

# -------------------------------
# BANDWIDTH SWEEP (Algorithm 2)
# -------------------------------
for B in bandwidths:
    file_name = f"SABP0_{B}_data.mat"
    file_path = os.path.join(DATA_DIR, file_name)

    if not os.path.exists(file_path):
        print(f"⚠️ Missing file: {file_name}")
        continue

    mat = sio.loadmat(file_path)

    # 🔴 CHANGE THIS VARIABLE NAME IF NEEDED
    P_peak = mat['peak_power'].flatten()

    # ---- SWH ----
    sorted_peaks = np.sort(P_peak)
    top_third = sorted_peaks[int(2 * len(sorted_peaks) / 3):]
    swh = np.mean(top_third)

    # ---- Max peak ----
    pmax = np.max(P_peak)

    # ---- Times Factor ----
    tf = pmax / swh

    # ---- Store ----
    valid_B.append(B)
    SWH.append(swh)
    Pmax.append(pmax)
    TimesFactor.append(tf)

    # -------------------------------
    # HISTOGRAM
    # -------------------------------
    plt.figure()
    plt.hist(P_peak / swh, bins=80, density=True)
    plt.axvline(rogue_threshold, linestyle='--', linewidth=2)
    plt.xlabel(r'$P_{\mathrm{peak}} / \mathrm{SWH}$')
    plt.ylabel('Probability Density')
    plt.title(f'Bandwidth = {B}')

    label = "Rogue Waves Present" if tf >= rogue_threshold else "No Rogue Waves"
    color = "red" if tf >= rogue_threshold else "green"

    plt.text(rogue_threshold + 0.1,
             0.8 * plt.ylim()[1],
             label,
             color=color)

    plt.show()

# -------------------------------
# SUMMARY PLOT
# -------------------------------
plt.figure()
plt.plot(valid_B, TimesFactor, 'o-')
plt.axhline(rogue_threshold, linestyle='--')
plt.xlabel('Filter Bandwidth Index')
plt.ylabel('Times Factor (Pmax / SWH)')
plt.title('Rogue-Wave Indicator vs Bandwidth')
plt.gca().invert_xaxis()
plt.show()
