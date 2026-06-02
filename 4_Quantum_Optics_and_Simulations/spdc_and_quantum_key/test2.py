import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# Constants
hbar = 1.0545718e-34  # Planck constant (J·s)
m0 = 9.10938356e-31   # Electron mass (kg)
eV_to_J = 1.60218e-19 # Conversion factor (eV to Joules)

# Material parameters for the quantum well
me = 0.067 * m0       # Effective mass of electron
mh_hh = 0.45 * m0     # Effective mass of heavy hole
mh_lh = 0.09 * m0     # Effective mass of light hole
Eg = 1.4 * eV_to_J    # Bandgap energy (e.g., GaAs)

# Strain-induced splitting
strain_split = 0.02 * eV_to_J  # Valence band splitting due to strain

# Quantum well parameters
well_width = 10e-9    # Well width (10 nm)
well_depth_CB = 0.3 * eV_to_J  # Conduction band offset
well_depth_VB = 0.2 * eV_to_J  # Valence band offset
mesh_points = 1000    # Spatial discretization

# Spatial grid
z = np.linspace(-well_width / 2, well_width / 2, mesh_points)
dz = z[1] - z[0]

# Define potential profiles for CB, HH, and LH
V_CB = np.zeros(mesh_points)
V_VB_hh = np.zeros(mesh_points)
V_VB_lh = np.zeros(mesh_points)

V_CB[np.abs(z) > well_width / 2] = well_depth_CB
V_VB_hh[np.abs(z) > well_width / 2] = well_depth_VB - strain_split / 2
V_VB_lh[np.abs(z) > well_width / 2] = well_depth_VB + strain_split / 2

# Hamiltonian function
def hamiltonian(m_eff, V):
    H = np.zeros((mesh_points, mesh_points))
    for i in range(mesh_points):
        if i > 0:
            H[i, i-1] = -hbar**2 / (2 * m_eff * dz**2)
        if i < mesh_points - 1:
            H[i, i+1] = -hbar**2 / (2 * m_eff * dz**2)
        H[i, i] = 2 * hbar**2 / (2 * m_eff * dz**2) + V[i]
    return H

# Solve the Schrödinger equation
H_e = hamiltonian(me, V_CB)
H_hh = hamiltonian(mh_hh, V_VB_hh)
H_lh = hamiltonian(mh_lh, V_VB_lh)

E_e, psi_e = eigh(H_e)
E_hh, psi_hh = eigh(H_hh)
E_lh, psi_lh = eigh(H_lh)

# Calculate transition probabilities
TE_prob = np.sum(np.abs(psi_e[:, 0] * psi_hh[:, 0])**2)  # Electron-HH
TM_prob = np.sum(np.abs(psi_e[:, 0] * psi_lh[:, 0])**2)  # Electron-LH

# Normalize probabilities
total_prob = TE_prob + TM_prob
TE_prob /= total_prob
TM_prob /= total_prob

# Plot results
plt.figure(figsize=(12, 6))

# Plot wavefunctions
plt.subplot(2, 1, 1)
plt.plot(z * 1e9, psi_e[:, 0]**2, label='Electron')
plt.plot(z * 1e9, psi_hh[:, 0]**2, label='Heavy Hole (HH)')
plt.plot(z * 1e9, psi_lh[:, 0]**2, label='Light Hole (LH)')
plt.title("Wavefunctions in Quantum Well")
plt.xlabel("Position (nm)")
plt.ylabel("Probability Density")
plt.legend()

# Plot emission probabilities
plt.subplot(2, 1, 2)
plt.bar(["TE (Electron-HH)", "TM (Electron-LH)"], [TE_prob, TM_prob], color=['blue', 'orange'])
plt.title("Photon Emission Probabilities (TE vs TM)")
plt.ylabel("Probability")

plt.tight_layout()
plt.show()
