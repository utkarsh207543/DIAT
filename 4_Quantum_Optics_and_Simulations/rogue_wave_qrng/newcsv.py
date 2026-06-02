import numpy as np
import scipy.io as sio
import glob
import csv
import re

# ===============================
# PARAMETERS
# ===============================
MIN_CURVE_LENGTH = 10
OUTPUT_CSV = "BW_vs_Figure_intensity.csv"

# ===============================
# HELPERS
# ===============================
def parse_bw_and_fig(filename):
    """
    SABP0_1_1_data.mat → BW = 0.1 , fig = 1
    """
    m = re.search(r"SABP(\d+)_(\d+)_(\d+)_data", filename)
    if not m:
        return None, None
    bw = f"{m.group(1)}.{m.group(2)}"
    fig = int(m.group(3))
    return bw, fig


def extract_intensity(matfile):
    data = sio.loadmat(matfile)
    if "Y" not in data:
        return None

    Y = data["Y"]
    curves = []

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
        curves.append(y)

    if len(curves) == 0:
        return None

    intensity = np.hstack(curves)
    intensity = intensity[np.isfinite(intensity)]
    return intensity


# ===============================
# COLLECT DATA
# ===============================
data_table = {}     # fig → {BW → intensity_string}
bw_set = set()

mat_files = sorted(glob.glob("*_data.mat"))
print(f"Found {len(mat_files)} files\n")

for file in mat_files:
    bw, fig = parse_bw_and_fig(file)
    if bw is None:
        print(f"[!] Skipping {file} (name mismatch)")
        continue

    intensity = extract_intensity(file)
    if intensity is None or len(intensity) == 0:
        print(f"[!] No valid data in {file}")
        continue

    bw_set.add(bw)

    if fig not in data_table:
        data_table[fig] = {}

    # store as space-separated string
    data_table[fig][bw] = " ".join(f"{v:.6g}" for v in intensity)

    print(f"✓ {file} → BW {bw} nm | Fig {fig} | {len(intensity)} samples")

# ===============================
# WRITE CSV
# ===============================
bw_list = sorted(bw_set, key=float)
fig_list = sorted(data_table.keys())

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)

    header = ["figure_id"] + [f"BW_{bw}" for bw in bw_list]
    writer.writerow(header)

    for fig in fig_list:
        row = [fig]
        for bw in bw_list:
            row.append(data_table[fig].get(bw, ""))
        writer.writerow(row)

print(f"\n[✓] CSV saved → {OUTPUT_CSV}")
