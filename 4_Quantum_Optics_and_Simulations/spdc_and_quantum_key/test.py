import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# Constants
hbar = 1.0545718e-34  # Planck constant (J·s)
m0 = 9.10938356e-31   # Electron mass (kg)
eV_to_J = 1.60218e-19 # Conversion factor (eV to Joules)

# Parameters
well_width = 10e-9  # Quantum well width (10 nm)
well_depth = 0.2    # Well depth in eV
strain = 0.01       # Compressive (-ve) or tensile (+ve) strain
mesh_points = 1000  # Spatial discretization

# Effective masses (different for heavy hole and light hole)
me = 0.067 * m0     # Electron mass in GaAs
mh_hh = 0.45 * m0   # Heavy-hole mass
mh_lh = 0.09 * m0   # Light-hole mass

# Spatial discretization
z = np.linspace(-well_width / 2, well_width / 2, mesh_points)
dz = z[1] - z[0]

# Potential profile for a simple square well
V = np.zeros(mesh_points)
V[np.abs(z) > well_width / 2] = well_depth * eV_to_J

# Hamiltonian matrix
def hamiltonian(m_eff):
    H = np.zeros((mesh_points, mesh_points))
    for i in range(mesh_points):
        if i > 0:
            H[i, i-1] = -hbar**2 / (2 * m_eff * dz**2)
        if i < mesh_points - 1:
            H[i, i+1] = -hbar**2 / (2 * m_eff * dz**2)
        H[i, i] = 2 * hbar**2 / (2 * m_eff * dz**2) + V[i]
    return H

# Solve for energy levels and wavefunctions
H_e = hamiltonian(me)
H_hh = hamiltonian(mh_hh)
H_lh = hamiltonian(mh_lh)

E_e, psi_e = eigh(H_e)
E_hh, psi_hh = eigh(H_hh)
E_lh, psi_lh = eigh(H_lh)

# Transition probabilities (simplified selection rules)
TE_prob = np.sum(np.abs(psi_e[:, 0] * psi_hh[:, 0])**2)
TM_prob = np.sum(np.abs(psi_e[:, 0] * psi_lh[:, 0])**2)

# Normalize probabilities
total_prob = TE_prob + TM_prob
TE_prob /= total_prob
TM_prob /= total_prob

# Plot wavefunctions and probabilities
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(z * 1e9, psi_e[:, 0]**2, label='Electron (E1)')
plt.plot(z * 1e9, psi_hh[:, 0]**2, label='HH (HH1)')
plt.plot(z * 1e9, psi_lh[:, 0]**2, label='LH (LH1)')
plt.title("Wavefunctions in the Quantum Well")
plt.xlabel("Position (nm)")
plt.ylabel("Probability Density")
plt.legend()

plt.subplot(2, 1, 2)
plt.bar(["TE", "TM"], [TE_prob, TM_prob], color=['blue', 'orange'])
plt.title("Photon Emission Probabilities")
plt.ylabel("Probability")

plt.tight_layout()
plt.show()
