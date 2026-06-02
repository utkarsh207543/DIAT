import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os


def read_ch1_ch2_timestamps(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ File not found: {filename}")

    ch1, ch2 = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('%') or not line.strip():
                continue
            try:
                source, timestamp = line.strip().split(',')
                timestamp = float(timestamp.strip())
                if int(source.strip()) == 1:
                    ch1.append(timestamp)
                elif int(source.strip()) == 2:
                    ch2.append(timestamp)
            except ValueError:
                continue

    return np.sort(ch1), np.sort(ch2)


def compute_symmetric_g2_fast(timestamps, bin_width, max_delay):
    delays = []
    for i, t in enumerate(timestamps):
        start = np.searchsorted(timestamps, t - max_delay, side='left')
        end = np.searchsorted(timestamps, t + max_delay, side='right')
        neighbors = timestamps[start:end]
        deltas = neighbors - t
        deltas = deltas[deltas != 0]
        delays.extend(deltas)
    delays = np.array(delays)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, edges = np.histogram(delays, bins=bins)
    tau = edges[:-1] + bin_width / 2
    g2 = hist / np.mean(hist) if np.mean(hist) > 0 else hist
    return tau, g2


def compute_cross_g2(ch1, ch2, bin_width, max_delay):
    delays = []
    for t in ch1:
        start = np.searchsorted(ch2, t - max_delay, side='left')
        end = np.searchsorted(ch2, t + max_delay, side='right')
        deltas = ch2[start:end] - t
        delays.extend(deltas)
    delays = np.array(delays)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, edges = np.histogram(delays, bins=bins)
    tau = edges[:-1] + bin_width / 2
    g2 = hist / np.mean(hist) if np.mean(hist) > 0 else hist
    return tau, g2


def antibunching_model(tau, tau_c):
    return 1 - np.exp(-np.abs(tau) / tau_c)


def fit_antibunching(tau, g2):
    try:
        popt, _ = curve_fit(antibunching_model, tau, g2, p0=[10e-9])
        return popt[0]
    except:
        return None


def plot_g2_with_fit(tau, g2, label="g²(τ)", zoom_ns=None):
    plt.figure(figsize=(8, 4))
    plt.plot(tau * 1e9, g2, drawstyle='steps-mid', label="Data")
    try:
        fit_range = np.abs(tau) < 100e-9
        tau_fit = tau[fit_range]
        g2_fit = g2[fit_range]
        tau_c = fit_antibunching(tau_fit, g2_fit)
        if tau_c:
            tau_fine = np.linspace(min(tau), max(tau), 1000)
            plt.plot(tau_fine * 1e9, antibunching_model(tau_fine, tau_c), 'r--',
                     label=f'Fit: τc = {tau_c * 1e9:.1f} ns')
    except Exception as e:
        print("Fit error:", e)

    plt.axvline(0, color='gray', linestyle='--')
    plt.xlabel("Delay τ (ns)")
    plt.ylabel("g²(τ)")
    plt.title(label)
    if zoom_ns:
        plt.xlim(-zoom_ns, zoom_ns)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def classify_g2(g2_0, label=""):
    print(f"\n📌 {label} → g²(0) = {g2_0:.3f}")
    if g2_0 < 0.95:
        print("🟣 Antibunching: Sub-Poissonian (quantum source)")
    elif g2_0 > 1.05:
        print("🟡 Bunching: Super-Poissonian (thermal source)")
    else:
        print("⚪ Poissonian: Coherent source (laser-like)")


def full_g2_fit_pipeline(filename, bin_width=1e-9, max_delay=100e-9, zoom_ns=50):
    print("📥 Loading data...")
    ch1, ch2 = read_ch1_ch2_timestamps(filename)
    print(f"✔️ Ch1 count: {len(ch1)} | Ch2 count: {len(ch2)}")

    print("\n🔁 Ch1 autocorrelation...")
    tau1, g2_1 = compute_symmetric_g2_fast(ch1, bin_width, max_delay)
    g2_0_ch1 = g2_1[np.argmin(np.abs(tau1))]
    classify_g2(g2_0_ch1, "Ch1")
    plot_g2_with_fit(tau1, g2_1, label="Ch1 g²(τ)", zoom_ns=zoom_ns)

    print("\n🔁 Ch2 autocorrelation...")
    tau2, g2_2 = compute_symmetric_g2_fast(ch2, bin_width, max_delay)
    g2_0_ch2 = g2_2[np.argmin(np.abs(tau2))]
    classify_g2(g2_0_ch2, "Ch2")
    plot_g2_with_fit(tau2, g2_2, label="Ch2 g²(τ)", zoom_ns=zoom_ns)

    print("\n🔁 Cross-correlation (Ch1 ↔ Ch2)...")
    tau_cross, g2_cross = compute_cross_g2(ch1, ch2, bin_width, max_delay)
    g2_0_cross = g2_cross[np.argmin(np.abs(tau_cross))]
    classify_g2(g2_0_cross, "Ch1-Ch2")
    plot_g2_with_fit(tau_cross, g2_cross, label="Ch1 ↔ Ch2 g²(τ)", zoom_ns=zoom_ns)


# 🚀 Run the pipeline (update filename as needed)
full_g2_fit_pipeline("test5_bs.csv", bin_width=1e-9, max_delay=100e-9, zoom_ns=50)
