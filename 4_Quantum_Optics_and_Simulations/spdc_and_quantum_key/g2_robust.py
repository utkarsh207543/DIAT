import numpy as np
import matplotlib.pyplot as plt
import re

# Optional fit dependency
try:
    from scipy.optimize import curve_fit
    _HAS_SCIPY = True
except Exception:
    _HAS_SCIPY = False

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
                src = int(parts[0]); ts = float(parts[1])
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

    zero_idx = np.argmin(np.abs(centers))
    g2_zero = g2[zero_idx]
    return centers, g2, g2_zero

# -----------------------------
# NEW: simple antibunching fit: g2(τ)=1 - C*exp(-|τ|/τ0)
# -----------------------------
def _g2_model(tau, C, tau0):
    return 1.0 - C * np.exp(-np.abs(tau) / tau0)

def fit_g2_antibunching(tau, g2_vals, dead_time=0.0, fit_max=None):
    """
    Least-squares fit to g2(τ)=1 - C*exp(-|τ|/τ0).
    Excludes |τ| < dead_time and, if fit_max is given, |τ| > fit_max to avoid side peaks.
    Returns (C, tau0, g20_fit) or (np.nan,... ) if fit fails or scipy unavailable.
    """
    if not _HAS_SCIPY:
        return np.nan, np.nan, np.nan

    tau = np.asarray(tau); g2 = np.asarray(g2_vals)
    m = np.isfinite(g2)
    if dead_time > 0:
        m &= (np.abs(tau) >= dead_time)
    if fit_max is not None:
        m &= (np.abs(tau) <= fit_max)

    x = tau[m]; y = g2[m]
    if x.size < 5:
        return np.nan, np.nan, np.nan

    # Initial guesses: C≈(1 - min g2), tau0≈a small fraction of fit window
    C0 = float(max(0.05, min(0.95, 1.0 - np.nanmin(y))))
    tau0_0 = float((np.nanmax(np.abs(x)) or 1e-9) / 5.0)

    try:
        popt, _ = curve_fit(_g2_model, x, y, p0=[C0, tau0_0], bounds=([0.0, 0.0],[1.5, np.inf]))
        C, tau0 = popt
        g20_fit = 1.0 - C
        return float(C), float(tau0), float(g20_fit)
    except Exception:
        return np.nan, np.nan, np.nan

# -----------------------------
# Step 3: Plot with optional fitted curve
# -----------------------------
def plot_g2(tau, g2_vals, fit_params=None, title="Single-detector g²(τ)"):
    if tau.size == 0:
        print("No data to plot.")
        return
    zi = np.argmin(np.abs(tau))
    plt.figure(figsize=(7.2, 4.0))
    plt.plot(tau*1e9, g2_vals, drawstyle="steps-mid", label="data")
    plt.axhline(1.0, ls=":", lw=1)
    plt.axvline(0.0, ls="--", lw=1)
    plt.scatter([tau[zi]*1e9], [g2_vals[zi]], zorder=3, label=f"g²(0) bin = {g2_vals[zi]:.2f}")

    if fit_params is not None and np.all(np.isfinite(fit_params)):
        C, tau0, g20_fit = fit_params
        # dense model curve over the same tau range
        tau_dense = np.linspace(tau.min(), tau.max(), 2000)
        g2_fit = _g2_model(tau_dense, C, tau0)
        plt.plot(tau_dense*1e9, g2_fit, lw=2, label=f"fit: g²(0)={g20_fit:.2f}, τ₀={tau0*1e9:.1f} ns")

    plt.xlim(tau.min()*1e9, tau.max()*1e9)
    plt.ylim(bottom=0)
    plt.xlabel("τ (ns)")
    plt.ylabel("g²(τ)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

# -----------------------------
# Step 4: Interpret g2(0)
# -----------------------------
def analyze_g2_zero(g20):
    print(f"🔍 g²(0) bin = {g20:.3f}")
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
def g2_pipeline(input_file, bin_width=2e-9, max_delay=100e-9, dead_time_ns=0.0,
                fit=True, fit_window_ns=None):
    print("📥 Reading Ch1 timestamps…")
    t = read_ch1_timestamps(input_file)
    print(f"✔️ Loaded {len(t)} timestamps")

    print("📊 Computing symmetric g²(τ)…")
    tau, g2_vals, g20 = compute_g2_symmetric(
        t, bin_width=bin_width, max_delay=max_delay, dead_time=dead_time_ns*1e-9
    )

    fit_params = None
    if fit and _HAS_SCIPY and tau.size:
        # Suggest a small window around 0 to avoid side peaks (e.g., ±20 ns)
        fit_max = None if fit_window_ns is None else fit_window_ns*1e-9
        fit_params = fit_g2_antibunching(
            tau, g2_vals, dead_time=dead_time_ns*1e-9, fit_max=fit_max
        )
        if np.all(np.isfinite(fit_params)):
            C, tau0, g20_fit = fit_params
            print(f"🧩 Fit result: g²(0)≈{g20_fit:.3f}, C≈{C:.3f}, τ₀≈{tau0*1e9:.2f} ns")
        else:
            print("Fit skipped/failed (install scipy or adjust fit window).")

    print("📈 Plotting…")
    plot_g2(tau, g2_vals, fit_params, title="Single-channel autocorrelation g²(τ)")

    print("📡 Interpreting g²(0)…")
    analyze_g2_zero(g20)

# -----------------------------
# Run
# -----------------------------
# Example: adjust dead_time_ns to your SPAD hold-off (e.g., 50–100 ns).
# Use a modest fit window (e.g., 20 ns) to avoid side peaks when fitting.
g2_pipeline("test.csv",
            bin_width=1e-10,      # 0.5 ns bins
            max_delay=20e-7,       # ±200 ns
            dead_time_ns=1,   # exclude |τ| < 136.5 ns
            fit=True,
            fit_window_ns=10)     # fit only |τ| <= 20 ns
