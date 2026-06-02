import numpy as np
import scipy.io as sio
import glob
import csv

# ===============================
# PARAMETERS
# ===============================
MIN_CURVE_LENGTH = 10
OUTPUT_CSV = "all_intensity_data.csv"

# ===============================
# FIND FILES
# ===============================
mat_files = sorted(glob.glob("*_data.mat"))
print(f"\nFound {len(mat_files)} data files\n")

if len(mat_files) == 0:
    raise RuntimeError("No *_data.mat files found")

# ===============================
# OPEN CSV
# ===============================
with open(OUTPUT_CSV, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Header
    writer.writerow(["file", "curve_id", "sample_id", "intensity"])

    # ===============================
    # MAIN LOOP
    # ===============================
    for file in mat_files:
        print(f"Processing {file} ...")

        data = sio.loadmat(file)

        if "Y" not in data:
            print(f"[!] Skipping {file} — no Y variable")
            continue

        Y = data["Y"]
        curves_written = 0

        for curve_id, y in enumerate(Y):
            y = np.squeeze(y)

            # -------- SAFE CHECKS --------
            if not isinstance(y, np.ndarray):
                continue
            if y.ndim != 1:
                continue
            if len(y) < MIN_CURVE_LENGTH:
                continue
            if np.all(np.isnan(y)):
                continue

            # -------- WRITE DATA --------
            for sample_id, val in enumerate(y):
                if np.isfinite(val):
                    writer.writerow([file, curve_id, sample_id, float(val)])
                    curves_written += 1

        print(f"    Saved {curves_written} samples\n")

print(f"[✓] ALL DATA SAVED → {OUTPUT_CSV}")
