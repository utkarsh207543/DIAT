import numpy as np
from scipy.integrate import quad
import matplotlib.pyplot as plt

# Constants
e = 1.6e-19       # elementary charge (C)
a0 = 5.29e-11     # Bohr radius (m)
epsilon0 = 8.85e-12
hbar = 1.05e-34

# Define radial wavefunctions for hydrogen-like orbitals (1D simplification)
def R_10(r):
    return 2 * (1/a0)**1.5 * np.exp(-r/a0)

def R_20(r):
    return (1 / (2 * np.sqrt(2))) * (1/a0)**1.5 * (2 - r/a0) * np.exp(-r/(2*a0))

def R_21(r):
    return (1 / (2 * np.sqrt(6))) * (1/a0)**1.5 * (r/a0) * np.exp(-r/(2*a0))

# Dipole matrix element: ⟨ψi | r | ψj⟩
def dipole_integral(Ri, Rj):
    integrand = lambda r: Ri(r) * r * Rj(r) * r**2  # r^3 due to volume element
    result, _ = quad(integrand, 0, 20*a0)
    return -e * result  # negative due to electron charge

# Compute dipole moments
mu_01 = dipole_integral(R_10, R_20)  # allowed: s → s
mu_12 = dipole_integral(R_20, R_21)  # allowed: s → p
mu_02 = dipole_integral(R_10, R_21)  # s → p

# Energy differences (simplified, in Joules)
E01 = 13.6 * e * (1 - 1/4)      # from n=1 to n=2
E12 = 13.6 * e * (1/4 - 1/9)    # from n=2 to n=3
E02 = 13.6 * e * (1 - 1/9)

# Calculate susceptibilities
def chi1(mu, E): return mu**2 / (epsilon0 * hbar * E)
def chi2(mu1, mu2, E1, E2): return mu1 * mu2 / (epsilon0 * hbar**2 * E1 * E2)
def chi3(mu, E): return mu**4 / (epsilon0 * hbar**3 * E**3)

# BBO (non-centrosymmetric, allow all transitions)
chi1_bbo = chi1(mu_01, E01)
chi2_bbo = chi2(mu_01, mu_12, E01, E12)
chi3_bbo = chi3(mu_01, E01)

# Glass (centrosymmetric, χ² = 0)
chi1_glass = chi1(mu_01, E01)
chi2_glass = 0
chi3_glass = chi3(mu_01, E01)

# Plotting
labels = ['χ¹', 'χ²', 'χ³']
bbo_vals = [chi1_bbo, chi2_bbo, chi3_bbo]
glass_vals = [chi1_glass, chi2_glass, chi3_glass]

x = np.arange(len(labels))
width = 0.35

plt.figure(figsize=(10, 6))
plt.bar(x - width/2, bbo_vals, width, label='BBO', color='royalblue')
plt.bar(x + width/2, glass_vals, width, label='Glass', color='gray')
plt.yscale('log')
plt.ylabel('Susceptibility (arb. units)')
plt.title('Nonlinear Susceptibilities χ for BBO vs Glass (Quantum Integration)')
plt.xticks(x, labels)
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()
