import pandas as pd
import numpy as np

# ===============================
# PARAMETERS
# ===============================
ROGUE_FACTOR = 4
CSV_FILE = "BW_vs_Figure_intensity.csv"
OUTPUT_TXT = "rogue_events_by_bandwidth.txt"
MIN_EVENTS = 100

# ===============================
# LOAD CSV
# ===============================
df = pd.read_csv(CSV_FILE)

bw_columns = [c for c in df.columns if c.startswith("BW_")]
bw_columns.sort(key=lambda x: float(x.replace("BW_", "")))

print(f"Found {len(bw_columns)} bandwidths\n")

# ===============================
# ROGUE EVENT ANALYSIS
# ===============================
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:

    for bw_col in bw_columns:
        bw = bw_col.replace("BW_", "")
        total_rogues = 0

        f.write(f"BW = {bw} nm\n")

        for _, row in df.iterrows():
            fig_id = int(row["figure_id"])
            cell = row[bw_col]

            if pd.isna(cell) or str(cell).strip() == "":
                continue

            # Convert space-separated string to array
            intensity = np.fromstring(str(cell), sep=" ")
            intensity = intensity[np.isfinite(intensity)]
            intensity = intensity[intensity > 0]

            if len(intensity) < MIN_EVENTS:
                continue

            # -------------------------------
            # SWH & THRESHOLD
            # -------------------------------
            sorted_I = np.sort(intensity)[::-1]
            top_third = sorted_I[:len(sorted_I) // 3]
            SWH = np.mean(top_third)
            threshold = ROGUE_FACTOR * SWH
            times_factor = threshold / SWH

            # -------------------------------
            # ROGUE EVENTS
            # -------------------------------
            rogues = np.sum(intensity > threshold)
            total_rogues += rogues

            if rogues > 0:
                f.write(
                    f"  Figure {fig_id} -> Rogue events: {rogues} "
                    f"(SWH={SWH:.3f}, Thr={threshold:.3f}, "
                    f"Thr/SWH={times_factor:.2f})\n"
                )

        if total_rogues == 0:
            f.write("  No rogue events detected\n")

        f.write("\n")

print(f"[OK] Rogue-event summary saved to '{OUTPUT_TXT}'")
