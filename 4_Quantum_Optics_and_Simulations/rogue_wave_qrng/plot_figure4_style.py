import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import glob
import os

ROGUE_FACTOR = 2.2
BINS = 60

mat_files = glob.glob("*_data.mat")

for file in mat_files:
    data = sio.loadmat(file)

    if "Y" not in data:
        continue

    Y = data["Y"]

    # -------------------------------
    # SAFE DATA EXTRACTION
    # -------------------------------
    curves = []
    for y in Y:
        y = np.squeeze(y)
        if isinstance(y, np.ndarray) and y.ndim == 1 and len(y) > 10:
            curves.append(y)

    if len(curves) == 0:
        continue

    intensity = np.hstack(curves)
    intensity = intensity[np.isfinite(intensity)]
    intensity = intensity[intensity > 0]

    if len(intensity) < 100:
        continue

    # -------------------------------
    # SWH CALCULATION
    # -------------------------------
    sorted_I = np.sort(intensity)[::-1]
    SWH = np.mean(sorted_I[:len(sorted_I)//3])
    threshold = ROGUE_FACTOR * SWH

    # -------------------------------
    # MAIN FIGURE
    # -------------------------------
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.hist(intensity, bins=BINS, log=True,
            color='#00E5EE', edgecolor='black')

    ax.axvline(SWH, color='red', linestyle='--', linewidth=2, label='SWH')
    ax.axvline(threshold, color='blue', linestyle='--',
               linewidth=2, label='2.2×SWH')

    ax.set_xlabel("Intensity (a.u.)")
    ax.set_ylabel("Number of Events")
    ax.legend()
    ax.set_xlim(left=0)

    # -------------------------------
    # INSET (WITHOUT BUILD-UP STATES)
    # -------------------------------
    inset = inset_axes(ax, width="35%", height="55%", loc="upper center")

    inset_data = intensity[intensity < threshold]

    inset.hist(inset_data, bins=25, log=True,
               color='gold', edgecolor='black')

    inset.axvline(SWH, color='red', linestyle='--', linewidth=1)
    inset.axvline(threshold, color='blue', linestyle='--', linewidth=1)

    inset.set_xlim(0, threshold * 1.1)
    inset.set_title("Inset", fontsize=9)
    inset.tick_params(labelsize=8)

    # -------------------------------
    # SAVE FIGURE
    # -------------------------------
    out_name = file.replace("_data.mat", "_Fig4_style.png")
    plt.tight_layout()
    plt.savefig(out_name, dpi=300)
    plt.close()

    print(f"[✓] Saved {out_name}")
