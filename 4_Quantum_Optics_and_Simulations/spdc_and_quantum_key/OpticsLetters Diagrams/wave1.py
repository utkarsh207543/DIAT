import numpy as np
from scipy.constants import hbar, e, m_e
from scipy.linalg import eigh
import matplotlib.pyplot as plt

# -----------------------------
# Quantum Well Parameters
# -----------------------------
L_well = 5e-9          # Well width (m)
V_well = -1.5 * e      # Well depth (J) [not used in infinite-well model below]
m_eff = 0.067 * m_e    # Effective mass of electron
num_levels = 4         # Number of energy levels to compute

# -----------------------------
# Potential: infinite square well via huge barriers
# -----------------------------
def potential(z, L):
    # 0 inside the well, very high outside (acts like infinite barriers)
    return np.where(np.abs(z) <= L / 2, 0.0, 1e10 * e)

# -----------------------------
# Solve the 1D Schrödinger Equation (finite-difference)
# -----------------------------
def solve_schrodinger(L, m, levels, N=1000):
    z = np.linspace(-L / 2, L / 2, N)
    dz = z[1] - z[0]
    V_z = potential(z, L)

    # Kinetic (second-derivative) operator with Dirichlet-like ends
    main_diag = np.full(N, -2.0)
    off_diag  = np.full(N - 1, 1.0)
    lap = (np.diag(main_diag) + np.diag(off_diag, k=1) + np.diag(off_diag, k=-1)) / (dz ** 2)
    T = -(hbar ** 2) / (2.0 * m) * lap

    # Hamiltonian
    H = T + np.diag(V_z)

    # Eigen-decomposition
    energies, wavefunctions = eigh(H)

    # Normalize eigenfunctions
    norms = np.sqrt(np.trapz(wavefunctions**2, z, axis=0))
    wavefunctions = wavefunctions / norms

    return energies[:levels], wavefunctions[:, :levels], z

# -----------------------------
# Transition dipole moment <ψ_i | z | ψ_j>
# -----------------------------
def dipole_moment(wavefunc1, wavefunc2, z):
    integrand = wavefunc1 * z * wavefunc2
    return np.trapz(integrand, z)

# -----------------------------
# Run solver
# -----------------------------
energies, wavefunctions, z = solve_schrodinger(L_well, m_eff, num_levels)

# Example TE/TM-like proxies from dipoles between a few states
# (Purely illustrative; real TE/TM selection rules need band-structure)
TE_dipole = abs(dipole_moment(wavefunctions[:, 0], wavefunctions[:, 1], z)) ** 2
TM_dipole = abs(dipole_moment(wavefunctions[:, 0], wavefunctions[:, 2], z)) ** 2

TE_prob = TE_dipole / (TE_dipole + TM_dipole)
TM_prob = TM_dipole / (TE_dipole + TM_dipole)

# -----------------------------
# Print results
# -----------------------------
print(f"Adjusted Well Depth (not used here): {V_well / e:.2f} eV")
print(f"TE Dipole Moment^2: {TE_dipole:.3e}")
print(f"TM Dipole Moment^2: {TM_dipole:.3e}")
print(f"TE Probability: {TE_prob:.3f}")
print(f"TM Probability: {TM_prob:.3f}")

# -----------------------------
# Plot wavefunctions with legend outside
# -----------------------------
fig, ax = plt.subplots(figsize=(8, 5))

for i in range(num_levels):
    ax.plot(z * 1e9, wavefunctions[:, i], label=f'ψ_{i + 1}')




ax.grid(False)

# Make room on the right for the legend
plt.subplots_adjust(right=0.75)

# Legend outside the axes on the right
legend = ax.legend(
    bbox_to_anchor=(1.02, 1.0),
    loc="upper left",
    borderaxespad=0.0
)

plt.show()
