import numpy as np

# -------------------------
# Parameters
# -------------------------
FILENAME = "Utkarsh_QRNG_10.txt"
COINCIDENCE_WINDOW = 5e-9# 5 ns

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
# Step 2: Fast coincidence count using searchsorted
# -------------------------
def count_coincidences_fast(reference, target, window):
    reference = np.asarray(reference)
    target = np.asarray(target)

    lower = np.searchsorted(target, reference - window, side='left')
    upper = np.searchsorted(target, reference + window, side='right')

    counts = upper - lower
    return np.sum(counts)

# -------------------------
# Step 3: Fast triple coincidences using logical masking
# -------------------------
def count_triple_coincidences_fast(T, A, B, window):
    A = np.asarray(A)
    B = np.asarray(B)

    # Check for at least one coincidence in A for each T
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

    # Normalize g²(0)
    g2 = (C_AB * 1.0) / (N_A * N_B) * N_A if (N_A * N_B) != 0 else 0
    return g2, C_AB

# -------------------------
# MAIN
# -------------------------
# Load and truncate
B, A, T = read_all_channels_and_truncate(FILENAME)

# Convert units if needed (optional)
# Uncomment if timestamps are in nanoseconds or ticks
A = A * 1e-9
B = B * 1e-9
T = T * 1e-9

print(f"✅ All channels truncated to same length: {len(A)} samples")

# Compute coincidence statistics
N_T = len(T)
N_TA = count_coincidences_fast(T, A, COINCIDENCE_WINDOW)
N_TB = count_coincidences_fast(T, B, COINCIDENCE_WINDOW)
N_TAB = count_triple_coincidences_fast(T, A, B, COINCIDENCE_WINDOW)

# Print results
print(f"\n🔸 Event Counts:")
print(f"  Total T                = {N_T}")
print(f"  Coincidences T & A     = {N_TA}")
print(f"  Coincidences T & B     = {N_TB}")
print(f"  Triple Coincidences    = {N_TAB}")

# Compute g²(0)
g2_0 = (N_TAB * N_T) / (N_TA * N_TB) if N_TA * N_TB != 0 else 0

print(f"\n📊 Normalized g²(0) GRA:")
print(f"g²(0) = (N_TAB × N_T) / (N_TA × N_TB)")
print(f"     = ({N_TAB} × {N_T}) / ({N_TA} × {N_TB})")
print(f"     = {g2_0:.4f}")

# Interpretation
if g2_0 < 1:
    print("🟢 g²(0) < 1 → Non-classical light (antibunched photons)")
elif np.isclose(g2_0, 1, atol=0.05):
    print("⚪ g²(0) ≈ 1 → Coherent light (laser-like)")
else:
    print("🟠 g²(0) > 1 → Classical light (thermal/bunched)")

# -------------------------
# HBT g²(0) Calculation
# -------------------------
g2_HBT, C_AB = compute_hbt_g2(A, B, COINCIDENCE_WINDOW)

print(f"\n🌟 HBT g²(0) between A and B:")
print(f"\n g2 = (C_AB * 1.0) / (N_A * N_B) * N_A ")
print(f"  Coincidences A & B     = {C_AB}")
print(f"  g²(0) = {g2_HBT:.4f}")

if g2_HBT < 1:
    print("🟢 HBT: Antibunched light (quantum)")
elif np.isclose(g2_HBT, 1, atol=0.05):
    print("⚪ HBT: Coherent light (laser-like)")
else:
    print("🟠 HBT: Bunched light (thermal/classical)")
