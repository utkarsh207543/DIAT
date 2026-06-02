import numpy as np
import matplotlib.pyplot as plt
import re

# -----------------------------
# Step 1: Read Ch1 timestamps (comma OR whitespace). Skips % headers.
# -----------------------------
_SPLIT = re.compile(r"[,\t ]+")

def read_ch1_timestamps(filename):
    t = []
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('%'):
                continue
            parts = _SPLIT.split(s)
            if len(parts) < 2:
                continue
            try:
                src = int(parts[0])
                ts  = float(parts[1])
            except ValueError:
                continue
            if src == 1:
                t.append(ts)
    return np.array(sorted(t), dtype=float)

# -----------------------------
# Step 2: Symmetric single-detector g2(τ) (auto-correlation)
# Normalization: g2(τ) = H(τ) / (R^2 * T * Δτ)
# dead_time filters |τ| < dead_time to suppress dead-time artifacts.
# -----------------------------
def compute_g2_symmetric(timestamps, bin_width=1e-9, max_delay=100e-9, dead_time=0.0):
    t = np.asarray(timestamps)
    if t.size < 2:
        return np.array([]), np.array([]), np.nan

    # Acquisition span and rate
    T = (t[-1] - t[0]) if t[-1] > t[0] else t[-1]
    if T <= 0:
        return np.array([]), np.array([]), np.nan
    R = t.size / T

    # Histogram bins centered around 0
    edges = np.arange(-max_delay, max_delay + bin_width, bin_width)
    centers = 0.5 * (edges[:-1] + edges[1:])
    H = np.zeros(centers.size, dtype=np.int64)

    # Fast two-pointer correlation (window-limited)
    N = t.size
    j0 = 0
    for i in range(N):
        ti = t[i]
        while j0 < N and t[j0] < ti - max_delay:
            j0 += 1
        j = j0
        while j < N and t[j] <= ti + max_delay:
            if j != i:
                dt = t[j] - ti
                if dead_time > 0.0 and abs(dt) < dead_time:
                    j += 1
                    continue
                idx = int(np.floor((dt - (-max_delay)) / bin_width))
                if 0 <= idx < H.size:
                    H[idx] += 1
            j += 1

    denom = (R * R * T * bin_width)
    g2 = H / denom if denom > 0 else np.full_like(H, np.nan, dtype=float)

    # g2(0) from the central bin
    zero_idx = np.argmin(np.abs(centers))
    g2_zero = g2[zero_idx]
    return centers, g2, g2_zero

# -----------------------------
# Step 3: Plot like the textbook figure (symmetric, dip at 0)
# -----------------------------
def plot_g2(tau, g2_vals, title="Single-detector g²(τ)"):
    if tau.size == 0:
        print("No data to plot.")
        return
    zi = np.argmin(np.abs(tau))
    plt.figure(figsize=(7.2, 4.0))
    plt.plot(tau*1e9, g2_vals, drawstyle="steps-mid")
    plt.axhline(1.0, ls=":", lw=1)          # reference at 1
    plt.axvline(0.0, ls="--", lw=1)         # τ = 0
    plt.scatter([tau[zi]*1e9], [g2_vals[zi]], zorder=3)
    plt.text(tau[zi]*1e9, g2_vals[zi], f"  g²(0)={g2_vals[zi]:.2f}", va="bottom")
    plt.xlim(-abs(tau).max()*1e9, abs(tau).max()*1e9)
    plt.ylim(bottom=0)
    plt.xlabel("τ (ns)")
    plt.ylabel("g²(τ)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# -----------------------------
# Step 4: Interpret g2(0)
# -----------------------------
def analyze_g2_zero(g20):
    print(f"🔍 g²(0) = {g20:.3f}")
    if np.isnan(g20):
        print("No g²(0) estimate (insufficient data).")
    elif g20 < 1:
        print("🟣 Antibunching (sub-Poissonian).")
    elif g20 > 1:
        print("🟡 Bunching (super-Poissonian).")
    else:
        print("⚪ Poissonian.")

# -----------------------------
# MAIN
# -----------------------------
def g2_pipeline(input_file, bin_width=2e-9, max_delay=100e-9, dead_time_ns=0.0):
    print("📥 Reading Ch1 timestamps…")
    t = read_ch1_timestamps(input_file)
    print(f"✔️ Loaded {len(t)} timestamps")

    print("📊 Computing symmetric g²(τ)…")
    tau, g2_vals, g20 = compute_g2_symmetric(
        t, bin_width=bin_width, max_delay=max_delay, dead_time=dead_time_ns*1e-9
    )

    print("📈 Plotting…")
    plot_g2(tau, g2_vals, title="Single-channel autocorrelation g²(τ)")

    print("📡 Interpreting g²(0)…")
    analyze_g2_zero(g20)

# -----------------------------
# Run
# -----------------------------
# Example: adjust dead_time_ns to your SPAD hold-off (e.g., 50–100 ns). Use 0 for SNSPD/very short dead time.
g2_pipeline("g2.csv", bin_width=5e-10, max_delay=2e-7, dead_time_ns=45)
