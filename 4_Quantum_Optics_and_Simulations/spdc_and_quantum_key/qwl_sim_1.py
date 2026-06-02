import numpy as np
from scipy.constants import hbar, e, m_e, pi, c
from scipy.integrate import quad

# Constants
m_eff = 0.067 * m_e  # Effective mass for GaAs in kg
E_gap = 1.424  # Bandgap energy for GaAs in eV
well_width = 10e-9  # Quantum well width in meters
eV_to_J = e  # Conversion factor: eV to Joules
h = hbar * 2 * pi

# 1. Solve Schrödinger's equation for energy levels in the quantum well
def energy_levels(n, m_eff, well_width):
    return (hbar**2 * pi**2 * n**2) / (2 * m_eff * well_width**2) / eV_to_J

# Compute energy levels for the first few quantum states
n_states = 3
energy_states = [energy_levels(n, m_eff, well_width) for n in range(1, n_states + 1)]

# 2. Calculate density of states
def density_of_states(E, E_n, m_eff):
    if E < E_n:
        return 0
    return (2 * np.sqrt(2 * m_eff**3 * (E - E_n))) / (pi**2 * hbar**3)

# 3. Calculate optical gain
def fermi_dirac(E, Ef, T):
    k_B = 1.38e-23  # Boltzmann constant in J/K
    exponent = (E - Ef) / (k_B * T)
    # Avoid overflow by using a threshold
    if exponent > 100:  # Large enough to approximate exp to infinity
        return 0
    return 1 / (np.exp(exponent) + 1)


def optical_gain(E, E_n, T, m_eff, Ef_c, Ef_v):
    return density_of_states(E, E_n, m_eff) * (fermi_dirac(E, Ef_c, T) - fermi_dirac(E, Ef_v, T))

# 4. Simulate gain spectrum
E_min, E_max = E_gap, E_gap + 0.1  # Energy range (in eV)
E_values = np.linspace(E_min, E_max, 100)
T = 300  # Temperature in Kelvin
Ef_c, Ef_v = 1.5, 1.3  # Example Fermi levels for conduction and valence bands

gain_spectrum = [optical_gain(E, energy_states[0], T, m_eff, Ef_c, Ef_v) for E in E_values]

# 5. Plot results
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.plot(E_values, gain_spectrum, label="Optical Gain")
plt.axvline(E_gap, color='r', linestyle='--', label="Bandgap")
plt.xlabel("Photon Energy (eV)")
plt.ylabel("Gain")
plt.title("Quantum Well Laser Optical Gain Spectrum")
plt.legend()
plt.grid()
plt.show()
