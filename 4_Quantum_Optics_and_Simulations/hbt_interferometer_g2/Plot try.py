import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Parameters
# -------------------------
FILENAME = "Utkarsh_QRNG_10.txt"
COINCIDENCE_WINDOW = 5e-9  # 5 ns

# -------------------------
# Step 1: Read and truncate all channels
# -------------------------
def read_all_channels_and_truncate(filename):
    B, A, T = [], [], []
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
                    B.append(int(parts[0]))  # Ch1 → B
                if parts[1] is not None:
                    A.append(int(parts[1]))  # Ch2 → A
                if parts[2] is not None:
                    T.append(int(parts[2]))  # Ch3 → T
            except ValueError:
                continue

    min_len = min(len(B), len(A), len(T))
    return (
        np.sort(np.array(B[:min_len])),
        np.sort(np.array(A[:min_len])),
        np.sort(np.array(T[:min_len]))
    )

# -------------------------
# Step 2: Coincidence Count
# -------------------------
def count_coincidences_fast(reference, target, window):
    reference = np.asarray(reference)
    target = np.asarray(target)

    lower = np.searchsorted(target, reference - window, side='left')
    upper = np.searchsorted(target, reference + window, side='right')

    counts = upper - lower
    return np.sum(counts)

# -------------------------
# Step 3: Triple Coincidences
# -------------------------
def count_triple_coincidences_fast(T, A, B, window):
    A = np.asarray(A)
    B = np.asarray(B)

    A_left = np.searchsorted(A, T - window, side='left')
    A_right = np.searchsorted(A, T + window, side='right')
    A_mask = (A_right > A_left)

    B_left = np.searchsorted(B, T - window, side='left')
    B_right = np.searchsorted(B, T + window, side='right')
    B_mask = (B_right > B_left)

    return np.sum(A_mask & B_mask)

# -------------------------
# HBT-style g²(0) between A and B
# -------------------------
def count_ab_coincidences(A, B, window):
    A = np.sort(np.asarray(A))
    B = np.sort(np.asarray(B))

    lower = np.searchsorted(B, A - window, side='left')
    upper = np.searchsorted(B, A + window, side='right')

    counts = upper - lower
    return np.sum(counts)

def compute_hbt_g2(A, B, window):
    N_A = len(A)
    N_B = len(B)
    C_AB = count_ab_coincidences(A, B, window)

    g2 = (C_AB * 1.0) / (N_A * N_B) * N_A if (N_A * N_B) != 0 else 0
    return g2, C_AB

# -------------------------
# MAIN
# -------------------------
# Load and truncate
B, A, T = read_all_channels_and_truncate(FILENAME)

# Convert ticks to seconds
A = A * 1e-9
B = B * 1e-9
T = T * 1e-9

print(f"✅ All channels truncated to same length: {len(A)} samples")

# Compute statistics
N_T = len(T)
N_TA = count_coincidences_fast(T, A, COINCIDENCE_WINDOW)
N_TB = count_coincidences_fast(T, B, COINCIDENCE_WINDOW)
N_TAB = count_triple_coincidences_fast(T, A, B, COINCIDENCE_WINDOW)

# GRA-style g²(0)
g2_0 = (N_TAB * N_T) / (N_TA * N_TB) if N_TA * N_TB != 0 else 0

# HBT-style g²(0)
g2_HBT, C_AB = compute_hbt_g2(A, B, COINCIDENCE_WINDOW)

# -------------------------
# PRINT RESULTS
# -------------------------
print(f"\n🔸 Event Counts:")
print(f"  Total T                = {N_T}")
print(f"  Coincidences T & A     = {N_TA}")
print(f"  Coincidences T & B     = {N_TB}")
print(f"  Triple Coincidences    = {N_TAB}")

print(f"\n📊 Normalized g²(0) GRA:")
print(f"g²(0) = ({N_TAB} × {N_T}) / ({N_TA} × {N_TB}) = {g2_0:.4f}")

print(f"\n🌟 HBT g²(0) between A and B:")
print(f"Coincidences A & B       = {C_AB}")
print(f"g²(0) = {g2_HBT:.4f}")

# -------------------------
# PLOTTING
# -------------------------
plt.figure(figsize=(12, 8))

# Time Histograms
plt.subplot(2, 2, 1)
plt.hist(A, bins=200, alpha=0.6, label='A')
plt.hist(B, bins=200, alpha=0.6, label='B')
plt.hist(T, bins=200, alpha=0.6, label='T')
plt.xlabel("Time (s)")
plt.ylabel("Counts")
plt.title("Time Distribution of Events")
plt.legend()

# Coincidence Counts Bar Chart
plt.subplot(2, 2, 2)
counts = [N_T, N_TA, N_TB, N_TAB]
labels = ['T', 'T ∩ A', 'T ∩ B', 'T ∩ A ∩ B']
bars = plt.bar(labels, counts, color='skyblue')
plt.title("Coincidence Event Counts")
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval}', ha='center', va='bottom')

# GRA g²(0)
plt.subplot(2, 2, 3)
plt.bar(["g²(0) GRA"], [g2_0], color='lightgreen')
plt.ylim(0, max(g2_0, g2_HBT, 1.5))
plt.title("GRA Normalized g²(0)")
plt.text(0, g2_0 + 0.05, f"{g2_0:.3f}", ha='center')

# HBT g²(0)
plt.subplot(2, 2, 4)
plt.bar(["g²(0) HBT"], [g2_HBT], color='lightcoral')
plt.ylim(0, max(g2_0, g2_HBT, 1.5))
plt.title("HBT Normalized g²(0)")
plt.text(0, g2_HBT + 0.05, f"{g2_HBT:.3f}", ha='center')

plt.tight_layout()
plt.show()
