import numpy as np
import os

# =========================================================
# 1. LOAD BITSTREAMS (same robust loader)
# =========================================================

def load_bits(filename):
    bits = []
    with open(filename, "r") as f:
        for line in f:
            for ch in line.strip():
                if ch == '0':
                    bits.append(0)
                elif ch == '1':
                    bits.append(1)
    return np.array(bits, dtype=np.uint8)

streams = {
    "SPDC": load_bits("SPDC.txt"),
    "QW": load_bits("QWL.txt"),
    "PHASE": load_bits("Phase.txt")
}

# Ensure equal length
N = min(len(b) for b in streams.values())
for k in streams:
    streams[k] = streams[k][:N]

print(f"Using {N:,} bits from each source")

# =========================================================
# 2. ENTROPY METRICS
# =========================================================

def min_entropy(bits):
    p = max(np.mean(bits), 1 - np.mean(bits))
    return -np.log2(p)

minH = {k: min_entropy(v) for k, v in streams.items()}

print("\nMin-Entropy per source:")
for k, v in minH.items():
    print(f"{k:6s}: {v:.6f}")

# =========================================================
# 3. ENTROPY-AWARE WEIGHTS
# =========================================================

total_H = sum(minH.values())
weights = {k: minH[k] / total_H for k in minH}

print("\nAdaptive fusion weights:")
for k, v in weights.items():
    print(f"{k:6s}: {v:.4f}")

# =========================================================
# 4. ENTROPY-AWARE FUSION (NO XOR)
# =========================================================

# Convert bits to {0,1} → probabilities
weighted_sum = (
    weights["SPDC"] * streams["SPDC"] +
    weights["QW"]   * streams["QW"] +
    weights["PHASE"]* streams["PHASE"]
)

# Threshold at 0.5
fused_bits = (weighted_sum >= 0.5).astype(np.uint8)

# =========================================================
# 5. SAVE FUSED BITSTREAM
# =========================================================

os.makedirs("fused_output", exist_ok=True)

with open("fused_output/fused_bits.txt", "w") as f:
    f.write("".join(map(str, fused_bits)))

print("\n✔ Fused bitstream saved to fused_output/fused_bits.txt")

# =========================================================
# 6. VERIFY FUSED RANDOMNESS
# =========================================================

def shannon_entropy(bits):
    p1 = np.mean(bits)
    p0 = 1 - p1
    eps = 1e-12
    return -(p0*np.log2(p0+eps) + p1*np.log2(p1+eps))

print("\n=== RANDOMNESS CHECK ===")
print(f"Fused Shannon entropy : {shannon_entropy(fused_bits):.6f}")
print(f"Fused Min-Entropy     : {min_entropy(fused_bits):.6f}")
print(f"Fused Bias            : {np.mean(fused_bits)-0.5:+.6e}")
