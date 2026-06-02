import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import glob
import os

# ===============================
# PARAMETERS
# ===============================
ROGUE_FACTOR = 2.2
MIN_CURVE_LENGTH = 10
HIST_BINS = 60

# ===============================
# OUTPUT STORAGE
# ===============================
qrng_bits = []

mat_files = sorted(glob.glob("*_data.mat"))

print(f"\nFound {len(mat_files)} data files\n")

# ===============================
# MAIN LOOP
# ===============================
for file in mat_files:
    print(f"Processing {file} ...")

    data = sio.loadmat(file)
    if "Y" not in data:
        print(f"[!] Skipping {file} — no Y data")
        continue

    Y = data["Y"]

    # -------------------------------
    # SAFE INTENSITY EXTRACTION
    # -------------------------------
    valid_curves = []

    for y in Y:
        y = np.squeeze(y)

        if not isinstance(y, np.ndarray):
            continue
        if y.ndim != 1:
            continue
        if len(y) < MIN_CURVE_LENGTH:
            continue
        if np.all(np.isnan(y)):
            continue

        valid_curves.append(y)

    if len(valid_curves) == 0:
        print(f"[!] Skipping {file} — no valid intensity vectors\n")
        continue

    intensity = np.hstack(valid_curves)

    # -------------------------------
    # SWH CALCULATION
    # -------------------------------
    intensity = intensity[np.isfinite(intensity)]
    intensity = intensity[intensity > 0]

    if len(intensity) < 100:
        print(f"[!] Skipping {file} — insufficient statistics\n")
        continue

    sorted_I = np.sort(intensity)[::-1]
    top_third = sorted_I[:len(sorted_I) // 3]
    SWH = np.mean(top_third)
    threshold = ROGUE_FACTOR * SWH

    # -------------------------------
    # EXTREME EVENTS
    # -------------------------------
    extreme_idx = np.where(intensity > threshold)[0]
    extreme_events = intensity[extreme_idx]

    print(f"    SWH = {SWH:.3f}")
    print(f"    Threshold (2.2×SWH) = {threshold:.3f}")
    print(f"    Extreme events = {len(extreme_events)}")

    if len(extreme_events) == 0:
        print()
        continue

    # -------------------------------
    # QRNG BIT GENERATION
    # -------------------------------
    # Parity extractor (replaceable)
    bits = extreme_idx % 2
    qrng_bits.extend(bits.tolist())

    # -------------------------------
    # PLOT HISTOGRAM
    # -------------------------------
    plt.figure(figsize=(7, 4))
    plt.hist(intensity, bins=HIST_BINS, log=True,
             color='cyan', edgecolor='black', alpha=0.85)

    plt.axvline(SWH, color='red', linestyle='--', linewidth=2, label='SWH')
    plt.axvline(threshold, color='blue', linestyle='--',
                linewidth=2, label='2.2×SWH')

    plt.xlabel("Intensity (a.u.)")
    plt.ylabel("Number of Events (log scale)")
    plt.title(file.replace("_data.mat", ""))
    plt.legend()
    plt.tight_layout()

    plot_name = file.replace("_data.mat", "_hist.png")
    plt.savefig(plot_name, dpi=300)
    plt.close()

    print(f"    Histogram saved → {plot_name}\n")

# ===============================
# SAVE QRNG OUTPUT
# ===============================
if len(qrng_bits) == 0:
    print("[!] No QRNG bits generated.")
else:
    with open("output.txt", "w") as f:
        bitstring = "".join(str(b) for b in qrng_bits)
        f.write(bitstring)

    print(f"\n[✓] QRNG COMPLETE")
    print(f"[✓] Total bits generated: {len(qrng_bits)}")
    print(f"[✓] Saved to output.txt")
