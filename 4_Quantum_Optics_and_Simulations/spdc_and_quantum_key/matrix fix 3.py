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
num_states = 10  # Number of energy states

# Function to calculate energy levels (in eV)
def energy_level(n, L, m):
    return (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2) / eV

# Compute energy levels
n_values = np.arange(1, num_states + 1)
E_conduction = np.array([energy_level(n, L, m_e) for n in n_values])
E_valence_hh = np.array([energy_level(n, L, m_hh) for n in n_values])
E_valence_lh = np.array([energy_level(n, L, m_hl) for n in n_values])

# Function to compute transition strength (simplified proportionality)
def transition_strength(n, type_):
    if type_ == "TE":
        return 1 / n**2  # TE mode scales inversely with quantum number squared
    elif type_ == "TM":
        return 1 / (n + 1)**2  # TM mode scales inversely with (n+1)^2

# Compute TE & TM transition strengths
te_values = np.array([transition_strength(n, "TE") for n in n_values])
tm_values = np.array([transition_strength(n, "TM") for n in n_values])

# Compute TM:TE Ratio (log scale)
tm_te_ratio = np.log10(tm_values / te_values)

# Plot all graphs in one figure
fig, axes = plt.subplots(3, 1, figsize=(8, 12))

# 1. Energy Levels Plot
axes[0].plot(n_values, E_conduction, "bo-", label="Conduction Band")
axes[0].plot(n_values, -E_valence_hh, "ro-", label="Valence Band (HH)")
axes[0].plot(n_values, -E_valence_lh, "go-", label="Valence Band (LH)")
axes[0].set_xlabel("Quantum State (n)")
axes[0].set_ylabel("Energy (eV)")
axes[0].set_title("Energy Levels in Quantum Well")
axes[0].legend()
axes[0].grid(True)

# 2. TE & TM Transition Strengths
axes[1].plot(n_values, te_values, "bo-", label="TE Transition Strength")
axes[1].plot(n_values, tm_values, "ro-", label="TM Transition Strength")
axes[1].set_xlabel("Quantum State (n)")
axes[1].set_ylabel("Transition Strength")
axes[1].set_title("TE & TM Transition Strengths")
axes[1].legend()
axes[1].grid(True)

# 3. TM:TE Ratio (Log Scale)
axes[2].plot(n_values, tm_te_ratio, "bo-", label="TM:TE Ratio")
axes[2].plot(n_values, np.interp(n_values, n_values, tm_te_ratio), "r--", label="Trend")
axes[2].set_xlabel("Quantum State (n)")
axes[2].set_ylabel("Log(TM:TE Ratio)")
axes[2].set_title("TM:TE Ratio vs. Number of States")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()
