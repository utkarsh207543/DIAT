import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# =============================================================================
# 1. Quantum Well and Material Parameters
# =============================================================================
L = 1e-9                   # Quantum well width (1 nm)
m0 = 9.10938356e-31        # Electron rest mass (kg)
m_e_eff = 0.067 * m0       # Conduction electron effective mass (e.g., GaAs)
hbar = 1.0545718e-34       # Reduced Planck's constant (J·s)

# Number of quantum states to compute
n_max = 10

# Calculate the conduction-band subband energies (in Joules) for an infinite square well:
# E_n = (n^2 * π^2 * ℏ^2) / (2 * m_e_eff * L^2)
n_values = np.arange(1, n_max + 1)
E_n = (n_values**2) * (np.pi**2 * hbar**2) / (2 * m_e_eff * L**2)  # in Joules
E_n_eV = E_n / 1.60218e-19  # Convert energy to electron volts (eV)

print("Conduction-Band Subband Energies (in eV):")
for n, E_val in zip(n_values, E_n_eV):
    print(f"  n = {n:2d}: {E_val:.3f} eV")

# =============================================================================
# 2. Mapping Voltage (or Injection Current) to the Number of Occupied States
# =============================================================================

# Define the voltage range for the simulation.
# We assume a threshold voltage V_th below which the laser does not operate.
V_th = 1.3    # Threshold voltage in volts
V_max = 2.0   # Maximum applied voltage (V)
N_points = 200
V_range = np.linspace(V_th, V_max, N_points)

# Define a mapping between voltage and the electron quasi-Fermi level.
# Assume a simple linear relation:
#    E_F = E_1 + α (V - V_th)
# where E_1 is the energy of the first subband and α is a scaling parameter.
alpha = 0.1 * 1.60218e-19  # 0.1 eV per Volt (converted to Joules per V)
E1 = E_n[0]               # Energy of the first subband (in Joules)
E_F = E1 + alpha * (V_range - V_th)  # Quasi-Fermi level in Joules
E_F_eV = E_F / 1.60218e-19         # Convert E_F to eV

# For each voltage value, count the number of conduction subband states
# that are below the quasi-Fermi level (i.e., considered occupied).
num_occupied_states = [np.sum(E_n <= EF) for EF in E_F]

# Map voltage to current by assuming a linear relation
# I = I0 * (V - V_th)
I0 = 500  # Scaling factor: 500 µA per Volt above threshold (arbitrary choice)
I_range = I0 * (V_range - V_th)  # Current in microamps (µA)

# Build a table (DataFrame) of the computed data
data = {
    "Voltage (V)": V_range,
    "Current (uA)": I_range,
    "Quasi-Fermi E (eV)": E_F_eV,
    "Occupied States": num_occupied_states
}
df = pd.DataFrame(data)
print("\nSample of the mapping data (first 10 rows):")
print(df.head(10))

# =============================================================================
# 3. Plotting the Results
# =============================================================================
plt.figure(figsize=(12, 8))

# Subplot 1: Number of Occupied States vs Voltage
plt.subplot(2, 1, 1)
plt.plot(V_range, num_occupied_states, 'bo-', label="Occupied States")
plt.xlabel("Voltage (V)")
plt.ylabel("Number of Occupied States")
plt.title("Mapping: Occupied Quantum Well States vs. Voltage")
plt.grid(True)
plt.legend()

# Subplot 2: Number of Occupied States vs. Current
plt.subplot(2, 1, 2)
plt.plot(I_range, num_occupied_states, 'ro-', label="Occupied States")
plt.xlabel("Current (uA)")
plt.ylabel("Number of Occupied States")
plt.title("Mapping: Occupied Quantum Well States vs. Injection Current")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
