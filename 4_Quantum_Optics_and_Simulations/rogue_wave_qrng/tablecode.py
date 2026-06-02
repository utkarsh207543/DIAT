import numpy as np
import scipy.io as sio
import glob
import csv
import re

# ===============================
# PARAMETERS
# ===============================
ROGUE_FACTOR = 2.2
MIN_CURVE_LENGTH = 10

# ===============================
# FIND FILES
# ===============================
mat_files = sorted(glob.glob("*_data.mat"))

table_rows = []

# ===============================
# MAIN LOOP
# ===============================
for file in mat_files:

    # -------------------------------
    # EXTRACT BANDWIDTH FROM FILENAME
    # -------------------------------
    match = re.search(r'(\d+)', file)
    bandwidth = int(match.group(1)) if match else None

    data = sio.loadmat(file)
    if "Y" not in data:
        continue

    Y = data["Y"]

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

    if not valid_curves:
        continue

    intensity = np.hstack(valid_curves)
    intensity = intensity[np.isfinite(intensity)]
    intensity = intensity[intensity > 0]

    if len(intensity) < 100:
        continue

    # -------------------------------
    # PEAK POWER (MEAN OF PER-CURVE MAXIMA)
    # -------------------------------
    curve_peaks = [
        np.max(y[np.isfinite(y) & (y > 0)])
        for y in valid_curves
    ]
    peak_power = np.mean(curve_peaks)

    # -------------------------------
    # SWH
    # -------------------------------
    sorted_I = np.sort(intensity)[::-1]
    top_third = sorted_I[:len(sorted_I) // 3]
    SWH = np.mean(top_third)

    # -------------------------------
    # TIMES FACTOR
    # -------------------------------
    times_factor = peak_power / SWH

    # -------------------------------
    # SAVE ROW
    # -------------------------------
    table_rows.append([
        bandwidth,
        round(peak_power, 1),
        round(SWH, 1),
        round(times_factor, 2)
    ])

# ===============================
# SORT BY BANDWIDTH (DESC)
# ===============================
table_rows.sort(reverse=True, key=lambda x: x[0])

# ===============================
# WRITE LATEX TABLE
# ===============================
with open("rogue_wave_table.tex", "w") as f:
    f.write("\\begin{table}[htbp]\n")
    f.write("\\centering\n")
    f.write("\\caption{Simulation results of comparison of peak wave height with significant wave height (SWH)}\n")
    f.write("\\label{tab:rogue_wave_bw}\n")
    f.write("\\renewcommand{\\arraystretch}{1.2}\n")
    f.write("\\begin{tabular}{c c c c}\n")
    f.write("\\hline\n")
    f.write("\\textbf{Bandwidth (nm)} & \\textbf{Peak Power (W)} & "
            "\\textbf{SWH (W)} & \\textbf{Times Factor} \\\\\n")
    f.write("\\hline\n")

    for r in table_rows:
        f.write(f"{r[0]} & {r[1]} & {r[2]} & {r[3]} \\\\\n")

    f.write("\\hline\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{table}\n")
