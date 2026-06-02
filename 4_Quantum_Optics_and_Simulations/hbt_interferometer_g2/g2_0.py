import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Parameters
# -------------------------
FILENAME = "Utkarsh_QRNG_10.txt"  # <-- Your file
COINCIDENCE_WINDOW = 5e-9         # 5 ns
BIN_WIDTH = 1e-9                  # 1 ns
MAX_DELAY = 50e-9                 # ±50 ns

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
# Step 3: g²(τ) Histogram Generator
# -------------------------
def time_difference_histogram(reference, target, bin_width, max_delay):
    delays = []
    for r in reference:
        nearby = target[(target >= r - max_delay) & (target <= r + max_delay)]
        delays.extend(nearby - r)
    bins = np.arange(-max_delay, max_delay + bin_width, bin_width)
    hist, _ = np.histogram(delays, bins=bins)
    centers = (bins[:-1] + bins[1:]) / 2
    return centers, hist / np.max(hist) if np.max(hist) > 0 else hist

# -------------------------
# Step 4: Run Pipeline
# -------------------------
A, B, T = read_channels(FILENAME)

# Count singles and coincidences
N_T = len(T)
N_TA = count_coincidences(T, A, COINCIDENCE_WINDOW)
N_TB = count_coincidences(T, B, COINCIDENCE_WINDOW)
N_TAB = count_triple_coincidences(T, A, B, COINCIDENCE_WINDOW)

# Compute unnormalized g² for plotting
tau_TA, g2_TA_arr = time_difference_histogram(T, A, BIN_WIDTH, MAX_DELAY)
tau_TB, g2_TB_arr = time_difference_histogram(T, B, BIN_WIDTH, MAX_DELAY)

# Compute normalized g²(0)
g2_0 = (N_TAB * N_T) / (N_TA * N_TB) if (N_TA * N_TB) != 0 else 0

# -------------------------
# Step 5: Plot g²(τ)
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
plt.savefig("g2_tau_plot.png", dpi=300)
print("📸 g²(τ) plots saved as 'g2_tau_plot.png'")

# -------------------------
# Step 6: Print Final Results
# -------------------------
print(f"\n🔸 Event Counts:")
print(f"  Total T    = {N_T}")
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
