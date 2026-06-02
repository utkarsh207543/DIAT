import numpy as np
import matplotlib.pyplot as plt

# Define polarization vectors
# Assuming propagation along z, so x = H, y = V
H = np.array([1, 0, 0])  # Horizontal polarization (x)
V = np.array([0, 1, 0])  # Vertical polarization (y)

# χ² tensor for BBO in contracted notation (3m symmetry, Kleinman approximation)
# Only non-zero components (in pm/V), values are approximate
# d_ij corresponds to χ²_ijk with Kleinman symmetry
d_eff = {
    "d31": 0.04,   # χ²_xyz or χ²_xzy
    "d32": 0.04,   # χ²_yzx or χ²_yxz
    "d33": 0.18,   # χ²_zzz
    "d24": 0.11,   # χ²_yzy or χ²_yyz
    "d15": 0.11,   # χ²_xzx or χ²_xxz
    "d22": 0.03    # χ²_yyy
}

# Define effective χ² calculation for Type-I process: pump -> signal + idler
# We define dot products of field polarizations with tensor symmetry
def calculate_chi2_eff(pump, signal, idler):
    # This function uses symmetry arguments to select the dominant tensor products
    # Assuming Kleinman symmetry: χ²_ijk = χ²_ikj
    eff = 0

    # χ²_xyz and permutations contribute if all directions are orthogonal
    if np.allclose(pump, H) and np.allclose(signal, V) and np.allclose(idler, V):
        eff = d_eff["d31"]  # χ²_xzz
    elif np.allclose(pump, V) and np.allclose(signal, H) and np.allclose(idler, H):
        eff = d_eff["d15"]  # χ²_yxx
    else:
        eff = 0  # Not allowed by crystal symmetry

    return eff

# List of pump polarizations and corresponding outputs
cases = [
    ("H", H, V, V),
    ("V", V, H, H),
    ("H (bad)", H, H, H),  # Not allowed
    ("V (bad)", V, V, V),  # Not allowed
]

# Calculate effective χ² values
labels = []
chi2_values = []

for label, pump, sig, idl in cases:
    eff = calculate_chi2_eff(pump, sig, idl)
    labels.append(label)
    chi2_values.append(eff)

# Plotting
plt.figure(figsize=(10, 5))
bar_colors = ['green' if val > 0 else 'red' for val in chi2_values]
plt.bar(labels, chi2_values, color=bar_colors)
plt.ylabel("Effective χ² (pm/V)")
plt.title("Effective χ² for SPDC in BBO (Type-I phase matching)")
plt.grid(axis='y', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()
