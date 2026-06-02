import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Parameters
# -------------------------
FILENAME = "Utkarsh_QRNG_10.txt"
COINCIDENCE_WINDOW = 5e-9  # 5 ns
BIN_WIDTH = 1e-9           # 1 ns
MAX_DELAY = 50e-9          # ±50 ns

# -------------------------
# Step 1: Read and truncate data
# -------------------------
def read_channels(filename):
    A, B, T = [], [], []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            parts = line.split()
            while len(parts) < 3:
                parts.append(None)
            try:
                if parts[0] is not None:
                    A.append(float(parts[0]))  # Ch1 → A
                if parts[1] is not None:
                    B.append(float(parts[1]))  # Ch2 → B
                if parts[2] is not None:
                    T.append(float(parts[2]))  # Ch3 → T
            except ValueError:
                continue
    min_len = min(len(A), len(B), len(T))
    return np.array(A[:min_len]), np.array(B[:min_len]), np.array(T[:min_len])

# -------------------------
# Step 2: Coincidence counters
# -------------------------
def count_coincidences(reference, target, window):
    count = 0
    i, j = 0, 0
    while i < len(reference) and j < len(target):
        dt = target[j] - reference[i]
        if abs(dt) <= window:
            count += 1
            i += 1
            j += 1
        elif dt < -window:
            j += 1
        else:
            i += 1
    return count

def count_triple_coincidences(T, A, B, window):
    count = 0
    for t in T:
        a_hit = np.any(np.abs(A - t) <= window)
        b_hit = np.any(np.abs(B - t) <= window)
        if a_hit and b_hit:
            count += 1
    return count

# -------------------------
# Step 3: Fast g²(τ) using FFT cross-correlation
# -------------------------
def fft_g2(reference, target, bin_width, max_delay):
    min_time = min(reference[0], target[0])
    max_time = max(reference[-1], target[-1])
    total_time = max_time - min_time

    num_bins = int(np.ceil(total_time / bin_width))
    time_axis = np.arange(num_bins) * bin_width + min_time

    ref_hist, _ = np.histogram(reference, bins=num_bins, range=(min_time, max_time))
    tgt_hist, _ = np.histogram(target, bins=num_bins, range=(min_time, max_time))

    corr = np.fft.ifft(np.fft.fft(ref_hist) * np.conj(np.fft.fft(tgt_hist))).real
    corr = np.fft.fftshift(corr)

    delay_axis = (np.arange(-num_bins//2, num_bins//2) * bin_width)
    mask = np.abs(delay_axis) <= max_delay
    norm_corr = corr[mask] / np.max(corr[mask]) if np.max(corr[mask]) > 0 else corr[mask]

    return delay_axis[mask], norm_corr

# -------------------------
# Step 4: Run Pipeline
# -------------------------
A, B, T = read_channels(FILENAME)

# Coincidence counts
N_T = len(T)
N_TA = count_coincidences(T, A, COINCIDENCE_WINDOW)
N_TB = count_coincidences(T, B, COINCIDENCE_WINDOW)
N_TAB = count_triple_coincidences(T, A, B, COINCIDENCE_WINDOW)

# g²(0)
g2_0 = (N_TAB * N_T) / (N_TA * N_TB) if (N_TA * N_TB) != 0 else 0

# g²(τ)
tau_TA, g2_TA_arr = fft_g2(T, A, BIN_WIDTH, MAX_DELAY)
tau_TB, g2_TB_arr = fft_g2(T, B, BIN_WIDTH, MAX_DELAY)

# -------------------------
# Step 5: Plot
# -------------------------
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(tau_TA * 1e9, g2_TA_arr, drawstyle='steps-mid')
plt.title(f'g²(τ) between T & A\n(g² ≈ {N_TA/N_T:.3f})')
plt.xlabel('Delay τ (ns)')
plt.ylabel('Normalized Coincidence')
plt.axhline(1, color='gray', linestyle='--')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(tau_TB * 1e9, g2_TB_arr, drawstyle='steps-mid')
plt.title(f'g²(τ) between T & B\n(g² ≈ {N_TB/N_T:.3f})')
plt.xlabel('Delay τ (ns)')
plt.ylabel('Normalized Coincidence')
plt.axhline(1, color='gray', linestyle='--')
plt.grid(True)

plt.tight_layout()
plt.savefig("g2_fft_tau_plot.png", dpi=300)
print("📸 g²(τ) plots saved as 'g2_fft_tau_plot.png'")

# -------------------------
# Step 6: Print Results
# -------------------------
print(f"\n🔸 Event Counts:")
print(f"  Total T              = {N_T}")
print(f"  Coincidences T & A   = {N_TA}")
print(f"  Coincidences T & B   = {N_TB}")
print(f"  Triple Coincidences  = {N_TAB}")

print(f"\n📊 Normalized g²(0):")
print(f"g²(0) = (N_TAB × N_T) / (N_TA × N_TB)")
print(f"     = ({N_TAB} × {N_T}) / ({N_TA} × {N_TB})")
print(f"     = {g2_0:.4f}")

if g2_0 < 1:
    print("🟢 g²(0) < 1 → Non-classical light (antibunched photons)")
elif np.isclose(g2_0, 1, atol=0.05):
    print("⚪ g²(0) ≈ 1 → Coherent light (laser-like)")
else:
    print("🟠 g²(0) > 1 → Classical light (thermal/bunched)")
