import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0545718e-34  # Reduced Planck constant, J·s
e = 1.60218e-19  # Elementary charge, C
m_e = 9.10938356e-31  # Electron mass, kg
E_gap = 1.424  # Bandgap energy for GaAs in eV
g_factor = 2.0  # Approximate g-factor for GaAs
mu_B = 9.274009994e-24  # Bohr magneton, J/T
B_field = 1.0  # Magnetic field strength in Tesla
delta_E_hyperfine = 1e-6  # Hyperfine splitting energy in eV

# Convert eV to Joules
eV_to_J = e

# 1. Energy levels with hyperfine splitting
E_base = E_gap * eV_to_J  # Bandgap energy in Joules
E_plus = E_base + delta_E_hyperfine * eV_to_J / 2  # Upper split level
E_minus = E_base - delta_E_hyperfine * eV_to_J / 2  # Lower split level

# 2. Zeeman splitting for spin states
E_zeeman_up = E_base + g_factor * mu_B * B_field / 2
E_zeeman_down = E_base - g_factor * mu_B * B_field / 2

# 3. Determine photon polarization modes
def photon_polarization(delta_E):
    # TE mode dominates for in-plane transitions
    # TM mode dominates for perpendicular transitions
    return "TE" if delta_E > 1e-3 * eV_to_J else "TM"

polarization_hyperfine = photon_polarization(delta_E_hyperfine * eV_to_J)
polarization_zeeman = photon_polarization(abs(E_zeeman_up - E_zeeman_down))

# 4. Visualization
energies = [E_minus, E_base, E_plus, E_zeeman_up, E_zeeman_down]
labels = ['E-', 'E_base', 'E+', 'E_zeeman_up', 'E_zeeman_down']

plt.figure(figsize=(8, 5))
plt.hlines(energies, 0, 1, colors=['r', 'k', 'b', 'g', 'g'], label=labels)
plt.text(1.05, E_minus, "E-", fontsize=10, color='r')
plt.text(1.05, E_plus, "E+", fontsize=10, color='b')
plt.text(1.05, E_zeeman_up, "E_zeeman_up", fontsize=10, color='g')
plt.text(1.05, E_zeeman_down, "E_zeeman_down", fontsize=10, color='g')
plt.xlabel("Relative Position")
plt.ylabel("Energy (J)")
plt.title("Hyperfine and Zeeman Splitting in Quantum Well Laser")
plt.grid()
plt.show()

# 5. Print results
print(f"Hyperfine Splitting Polarization Mode: {polarization_hyperfine}")
print(f"Zeeman Splitting Polarization Mode: {polarization_zeeman}")
