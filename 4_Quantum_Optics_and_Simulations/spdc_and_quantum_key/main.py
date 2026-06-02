# =========================================================
# CPRCT: Cross-Physical Randomness Consistency Test
# FINAL, STABLE, PUBLICATION-READY VERSION
# =========================================================

import numpy as np
import matplotlib
matplotlib.use("Agg")   # SAFE backend (no PyCharm crashes)
import matplotlib.pyplot as plt
from itertools import combinations
import os

# =========================================================
# 1. ROBUST BITSTREAM LOADER
# =========================================================

def load_bits(filename):
    bits = []
    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            for ch in line:
                if ch == '0':
                    bits.append(0)
                elif ch == '1':
                    bits.append(1)
                else:
                    raise ValueError(
                        f"Invalid character '{ch}' in {filename}"
                    )
    return np.array(bits, dtype=np.uint8)

# =========================================================
# 2. ENTROPY & BASIC METRICS
# =========================================================

def shannon_entropy(bits):
    p1 = np.mean(bits)
    p0 = 1.0 - p1
    eps = 1e-12
    return -(p0*np.log2(p0+eps) + p1*np.log2(p1+eps))

def min_entropy(bits):
    p = max(np.mean(bits), 1.0 - np.mean(bits))
    return -np.log2(p)

def bit_bias(bits):
    return np.mean(bits) - 0.5

# =========================================================
# 3. AUTOCORRELATION
# =========================================================

def autocorr(bits, lag=1):
    if lag >= len(bits):
        return np.nan
    b = bits - np.mean(bits)
    return np.corrcoef(b[:-lag], b[lag:])[0, 1]

def autocorr_curve(bits, max_lag=100):
    return [autocorr(bits, lag=i) for i in range(1, max_lag+1)]

# =========================================================
# 4. CROSS-CORRELATION
# =========================================================

def cross_corr(bits1, bits2):
    n = min(len(bits1), len(bits2))
    return np.corrcoef(bits1[:n], bits2[:n])[0, 1]

# =========================================================
# 5. TEMPORAL STABILITY
# =========================================================

def entropy_segments(bits, segments=10):
    seg_len = len(bits) // segments
    return [
        shannon_entropy(bits[i*seg_len:(i+1)*seg_len])
        for i in range(segments)
    ]

# =========================================================
# 6. LOAD DATA
# =========================================================

qrng_files = {
    "SPDC": "SPDC.txt",
    "QW_TOA": "QWL.txt",
    "PHASE": "Phase.txt"
}

streams = {k: load_bits(v) for k, v in qrng_files.items()}

print("\n=== DATA LOADED ===")
for k, b in streams.items():
    print(f"{k:7s} | {len(b):,} bits | mean={np.mean(b):.6f}")

# =========================================================
# 7. CRITICAL IDENTITY CHECK (VERY IMPORTANT)
# =========================================================

print("\n=== IDENTITY CHECK ===")
for (n1, b1), (n2, b2) in combinations(streams.items(), 2):
    identical = np.array_equal(b1, b2)
    print(f"{n1:7s} == {n2:7s} : {identical}")
    if identical:
        print(f"⚠️  WARNING: {n1} and {n2} are BIT-FOR-BIT IDENTICAL!\n")

# =========================================================
# 8. CPRCT ANALYSIS
# =========================================================

results = {}

for name, bits in streams.items():
    results[name] = {
        "Shannon": shannon_entropy(bits),
        "MinEntropy": min_entropy(bits),
        "Bias": bit_bias(bits),
        "Autocorr1": autocorr(bits, lag=1),
        "Segments": entropy_segments(bits),
        "AutocorrCurve": autocorr_curve(bits)
    }

# =========================================================
# 9. CROSS-CORRELATION
# =========================================================

cross_results = {}
for (n1, b1), (n2, b2) in combinations(streams.items(), 2):
    cross_results[f"{n1}-{n2}"] = cross_corr(b1, b2)

# =========================================================
# 10. PRINT SUMMARY (TABLE-READY)
# =========================================================

print("\n=== CPRCT SUMMARY ===")
for k, v in results.items():
    print(f"\n{k}")
    print(f"  Shannon entropy     : {v['Shannon']:.6f}")
    print(f"  Min-entropy         : {v['MinEntropy']:.6f}")
    print(f"  Bias                : {v['Bias']:.6e}")
    print(f"  Autocorr (lag=1)    : {v['Autocorr1']:.6e}")

print("\n=== CROSS-CORRELATION ===")
for k, v in cross_results.items():
    print(f"  {k:15s}: {v:.6e}")

# =========================================================
# 11. CREATE OUTPUT DIRECTORY
# =========================================================

os.makedirs("figures", exist_ok=True)

# =========================================================
# 12. FIGURE 1 – ENTROPY COMPARISON
# =========================================================

labels = list(results.keys())
shannon_vals = [results[k]["Shannon"] for k in labels]
min_vals = [results[k]["MinEntropy"] for k in labels]
x = np.arange(len(labels))

plt.figure(figsize=(7,5))
plt.bar(x - 0.15, shannon_vals, 0.3, label="Shannon Entropy")
plt.bar(x + 0.15, min_vals, 0.3, label="Min-Entropy")
plt.xticks(x, labels)
plt.ylabel("Entropy per bit")
plt.title("Cross-Physical Randomness Consistency Test")
plt.legend()
plt.tight_layout()
plt.savefig("figures/entropy_comparison.png", dpi=300)
plt.close()

# =========================================================
# 13. FIGURE 2 – TEMPORAL STABILITY
# =========================================================

plt.figure(figsize=(7,5))
for k in results:
    plt.plot(results[k]["Segments"], marker='o', label=k)

plt.xlabel("Segment index")
plt.ylabel("Entropy per bit")
plt.title("Temporal Stability of Entropy")
plt.legend()
plt.tight_layout()
plt.savefig("figures/entropy_stability.png", dpi=300)
plt.close()

# =========================================================
# 14. FIGURE 3 – AUTOCORRELATION DECAY
# =========================================================

plt.figure(figsize=(7,5))
for k in results:
    plt.plot(results[k]["AutocorrCurve"], label=k)

plt.yscale("symlog")
plt.xlabel("Lag")
plt.ylabel("Autocorrelation")
plt.title("Autocorrelation Decay")
plt.legend()
plt.tight_layout()
plt.savefig("figures/autocorrelation_decay.png", dpi=300)
plt.close()

print("\n✔ Analysis complete.")
print("✔ Figures saved in ./figures/")

# =========================================================
# 11.5 SAVE PLOTTING DATA (LATEX / PGFPLOTS READY)
# =========================================================

os.makedirs("plot_data", exist_ok=True)

# ---------------------------------------------------------
# FILE 1: ENTROPY COMPARISON
# Columns: Source, Shannon, MinEntropy
# ---------------------------------------------------------

with open("plot_data/entropy_comparison.dat", "w") as f:
    f.write("#Source Shannon MinEntropy\n")
    for k in labels:
        f.write(f"{k} {results[k]['Shannon']} {results[k]['MinEntropy']}\n")

print("✔ Saved: plot_data/entropy_comparison.dat")


# ---------------------------------------------------------
# FILE 2: TEMPORAL STABILITY
# Columns: Segment SPDC QW_TOA PHASE
# ---------------------------------------------------------

num_segments = len(next(iter(results.values()))["Segments"])

with open("plot_data/entropy_stability.dat", "w") as f:
    header = "#Segment " + " ".join(results.keys()) + "\n"
    f.write(header)

    for i in range(num_segments):
        row = [str(i)]
        for k in results:
            row.append(str(results[k]["Segments"][i]))
        f.write(" ".join(row) + "\n")

print("✔ Saved: plot_data/entropy_stability.dat")


# ---------------------------------------------------------
# FILE 3: AUTOCORRELATION DECAY
# Columns: Lag SPDC QW_TOA PHASE
# ---------------------------------------------------------

max_lag = len(next(iter(results.values()))["AutocorrCurve"])

with open("plot_data/autocorr_decay.dat", "w") as f:
    header = "#Lag " + " ".join(results.keys()) + "\n"
    f.write(header)

    for i in range(max_lag):
        row = [str(i+1)]
        for k in results:
            row.append(str(results[k]["AutocorrCurve"][i]))
        f.write(" ".join(row) + "\n")

print("✔ Saved: plot_data/autocorr_decay.dat")
