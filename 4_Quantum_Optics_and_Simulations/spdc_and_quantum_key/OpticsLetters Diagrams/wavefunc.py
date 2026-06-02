import numpy as np
from scipy.constants import hbar, e, m_e
from scipy.linalg import eigh
import matplotlib.pyplot as plt

# Quantum Well Parameters
L_well = 5e-9  # Well width in meters
V_well = -1.5 * e  # Well depth in Joules
m_eff = 0.067 * m_e  # Effective mass of electron
num_levels = 5
# Number of energy levels to compute

# Define potential well
def potential(z, L):
    return np.where(np.abs(z) <= L / 2, 0, 1e10 * e)  # High outside the well

# Solve the 1D Schrödinger Equation
def solve_schrodinger(L, V, m, levels):
    N = 1000
    z = np.linspace(-L / 2, L / 2, N)
    dz = z[1] - z[0]
    V_z = potential(z, L)

    # Build Hamiltonian
    T = (-hbar ** 2 / (2 * m * dz ** 2)) * (-2 * np.eye(N) + np.eye(N, k=1) + np.eye(N, k=-1))
    H = T + np.diag(V_z)

    # Solve for eigenvalues and eigenvectors
    energies, wavefunctions = eigh(H)

    # Normalize wavefunctions
    wavefunctions = wavefunctions / np.sqrt(np.trapz(wavefunctions**2, z, axis=0))

    # Return first 'levels' energy levels and wavefunctions
    return energies[:levels], wavefunctions[:, :levels], z

# Calculate transition dipole moments
def dipole_moment(wavefunc1, wavefunc2, z):
    integrand = wavefunc1 * z * wavefunc2
    return np.trapz(integrand, z)

# Solve Schrödinger equation for the quantum well
energies, wavefunctions, z = solve_schrodinger(L_well, V_well, m_eff, num_levels)

# Compute transition dipole moments
TE_dipole = abs(dipole_moment(wavefunctions[:, 0], wavefunctions[:, 1], z)) ** 2
TM_dipole = abs(dipole_moment(wavefunctions[:, 0], wavefunctions[:, 2], z)) ** 2

# Normalize probabilities
TE_prob = TE_dipole / (TE_dipole + TM_dipole)
TM_prob = TM_dipole / (TE_dipole + TM_dipole)

# Display Results
print(f"Adjusted Well Depth: {V_well / e:.2f} eV")
print(f"TE Dipole Moment^2: {TE_dipole:.3e}")
print(f"TM Dipole Moment^2: {TM_dipole:.3e}")
print(f"TE Probability: {TE_prob:.3f}")
print(f"TM Probability: {TM_prob:.3f}")

# Visualization of wavefunctions
plt.figure(figsize=(8, 5))
for i in range(num_levels):
    plt.plot(z * 1e9, wavefunctions[:, i], label=f'ψ_{i + 1} (E={energies[i] / e:.3f} eV)')
plt.title("Quantum Well Wavefunctions (Adjusted Well Depth)")
plt.xlabel("Position (nm)")
plt.ylabel("Wavefunction Amplitude")
plt.legend()
plt.grid()
plt.show()

