import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0545718e-34  # Reduced Planck's constant (Joule*seconds)
m_e = 9.10938356e-31  # Electron mass (kg)
m_hh = 0.5 * m_e  # Heavy hole effective mass (kg)
m_hl = 0.25 * m_e  # Light hole effective mass (kg)
eV = 1.60218e-19  # Electron volt (Joules)

# Quantum well parameters
L = 5e-9  # Quantum well width (meters)
num_states = 2  # Number of energy states

# External field for asymmetry (strain/magnetic field)
B_field = 2  # Tesla
strain_effect = 0.05  # Strain factor

# Function to calculate energy levels (in eV)
def energy_level(n, L, m):
    return (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2) / eV

# Function to compute transition strength (simplified proportionality)
def transition_strength(n, type_):
    if type_ == "TE":
        return 1 / n**2  # TE mode scales inversely with quantum number squared
    elif type_ == "TM":
        return 1 / (n + 1)**2  # TM mode scales inversely with (n+1)^2

# Compute TM:TE Ratio
n_values = np.arange(1, num_states + 1)
te_values = np.array([transition_strength(n, "TE") for n in n_values])
tm_values = np.array([transition_strength(n, "TM") for n in n_values])

tm_te_ratio = np.log10(tm_values / te_values)  # Log scale for TM:TE ratio

# Plot the TM:TE Ratio
plt.figure(figsize=(8, 5))
plt.plot(n_values, tm_te_ratio, marker="o", linestyle="-", color="blue", label="TM:TE Ratio")
plt.plot(n_values, np.interp(n_values, n_values, tm_te_ratio), "r--", label="Trend")

# Formatting
plt.xlabel("Number of States (n)", fontsize=12)
plt.ylabel("Log(TM:TE Ratio)", fontsize=12)
plt.title("TM:TE Ratio vs. Number of States", fontsize=14)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.show()
