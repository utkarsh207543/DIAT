import pandas as pd
import numpy as np

# ===============================
# PARAMETERS
# ===============================
ROGUE_FACTOR = 2.2
CSV_FILE = "BW_vs_Figure_intensity.csv"
OUTPUT_TXT = "rogue_events_by_bandwidth_physics_corrected.txt"

MIN_EVENTS_TOTAL = 500     # per BW
MIN_EVENTS_FIG = 50        # per figure
KURTOSIS_THRESHOLD = 0.0  # >0 = heavy-tailed

# ===============================
# KURTOSIS (NO SCIPY)
# ===============================
def excess_kurtosis(x):
    x = np.asarray(x)
    mu = np.mean(x)
    sigma = np.std(x, ddof=0)

    if sigma == 0:
        return -3.0   # degenerate distribution

    m4 = np.mean((x - mu) ** 4)
    return m4 / (sigma ** 4) - 3.0


# ===============================
# LOAD CSV
# ===============================
df = pd.read_csv(CSV_FILE)

bw_columns = [c for c in df.columns if c.startswith("BW_")]
bw_columns.sort(key=lambda x: float(x.replace("BW_", "")))

print(f"Found {len(bw_columns)} bandwidths\n")

# ===============================
# PHYSICS-AWARE ROGUE ANALYSIS
# ===============================
with open(OUTPUT_TXT, "w", encoding="utf-8") as f:

    for bw_col in bw_columns:
        bw = bw_col.replace("BW_", "")

        all_intensity = []
        fig_data = {}

        # -------------------------------
        # COLLECT DATA
        # -------------------------------
        for _, row in df.iterrows():
            fig_id = int(row["figure_id"])
            cell = row[bw_col]

            if pd.isna(cell) or str(cell).strip() == "":
                continue

            intensity = np.fromstring(str(cell), sep=" ")
            intensity = intensity[np.isfinite(intensity)]
            intensity = intensity[intensity > 0]

            if len(intensity) < MIN_EVENTS_FIG:
                continue

            fig_data[fig_id] = intensity
            all_intensity.append(intensity)

        if len(all_intensity) == 0:
            continue

        all_intensity = np.hstack(all_intensity)

        if len(all_intensity) < MIN_EVENTS_TOTAL:
            continue

        # -------------------------------
        # STATISTICAL REGIME CHECK
        # -------------------------------
        ex_kurt = excess_kurtosis(all_intensity)

        f.write(f"BW = {bw} nm\n")
        f.write(f"  Total samples = {len(all_intensity)}\n")
        f.write(f"  Excess kurtosis = {ex_kurt:.3f}\n")

        # -------------------------------
        # GAUSSIAN / STATIONARY REGIME
        # -------------------------------
        if ex_kurt <= KURTOSIS_THRESHOLD:
            f.write(
                "  Regime: Stationary / Gaussian-like\n"
                "  Rogue-wave criterion not applicable\n\n"
            )
            continue

        # -------------------------------
        # ROGUE-CAPABLE REGIME
        # -------------------------------
        sorted_I = np.sort(all_intensity)[::-1]
        top_third = sorted_I[:len(sorted_I) // 3]
        SWH = np.mean(top_third)
        threshold = ROGUE_FACTOR * SWH

        f.write(
            "  Regime: Intermittent / Heavy-tailed\n"
            f"  BW-level SWH = {SWH:.3f}\n"
            f"  Threshold = {threshold:.3f}\n"
            f"  Thr/SWH = {threshold / SWH:.2f}\n"
        )

        total_rogues = 0

        for fig_id, intensity in fig_data.items():
            rogues = np.sum(intensity > threshold)
            total_rogues += rogues

            if rogues > 0:
                f.write(
                    f"    Figure {fig_id} -> Rogue events: {rogues}\n"
                )

        if total_rogues == 0:
            f.write("    No rogue events detected\n")

        f.write("\n")

print(f"[OK] Physics-correct rogue analysis saved to '{OUTPUT_TXT}'")
