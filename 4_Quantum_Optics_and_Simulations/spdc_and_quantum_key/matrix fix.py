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
num_states = 10  # Number of energy states to consider

# External field to introduce asymmetry (e.g., magnetic field in Tesla)
B_field = 2  # Tesla (arbitrary value)
strain_effect = 0.05  # Arbitrary strain factor


# Function to calculate energy levels (in eV)
def energy_level(n, L, m):
    return (n ** 2 * np.pi ** 2 * hbar ** 2) / (2 * m * L ** 2) / eV


# Function to calculate the position matrix element ⟨HH|x|HL⟩
def position_matrix_element(n_hh, n_hl, L):
    if (n_hh + n_hl) % 2 == 0:
        return 0  # Integral is zero for even sums
    else:
        return (-2 * L / (np.pi ** 2) * (1 / (n_hh ** 2 - n_hl ** 2)))


# Function to calculate emission probabilities with asymmetry
def emission_probabilities(n_hh, n_hl, L, B_field, strain_effect):
    matrix_element = position_matrix_element(n_hh, n_hl, L)

    # Introduce asymmetry: σ+ and σ− influenced differently by external fields
    sigma_plus = (matrix_element ** 2) * (1 + 0.1 * B_field) * (1 + strain_effect)
    sigma_minus = (matrix_element ** 2) * (1 - 0.1 * B_field) * (1 - strain_effect)

    return sigma_plus, sigma_minus


# Compute energy levels
energies_hh = [energy_level(n, L, m_hh) for n in range(1, num_states + 1)]
energies_hl = [energy_level(n, L, m_hl) for n in range(1, num_states + 1)]

# Compute emission probabilities
sigma_plus_probs = np.zeros((num_states, num_states))
sigma_minus_probs = np.zeros((num_states, num_states))

for n_hh in range(1, num_states + 1):
    for n_hl in range(1, num_states + 1):
        sigma_plus, sigma_minus = emission_probabilities(n_hh, n_hl, L, B_field, strain_effect)
        sigma_plus_probs[n_hh - 1, n_hl - 1] = sigma_plus
        sigma_minus_probs[n_hh - 1, n_hl - 1] = sigma_minus

# Compute the difference in emission probability
sigma_difference = sigma_plus_probs - sigma_minus_probs
overall_dominant_emission = np.maximum(sigma_plus_probs, sigma_minus_probs)

# Print computed energy levels
print("Heavy Hole (HH) Energy Levels (eV):", np.round(energies_hh, 3))
print("Light Hole (HL) Energy Levels (eV):", np.round(energies_hl, 3))

# Plot results
fig, axs = plt.subplots(1, 4, figsize=(24, 6))

# Plot σ+ Emission Probabilities
axs[0].imshow(sigma_plus_probs, cmap="viridis", origin="lower")
axs[0].set_title(r"$\sigma^+$ Emission Probabilities")
axs[0].set_xlabel("Light Hole State (n_hl)")
axs[0].set_ylabel("Heavy Hole State (n_hh)")
plt.colorbar(axs[0].imshow(sigma_plus_probs, cmap="viridis", origin="lower"), ax=axs[0])

# Plot σ− Emission Probabilities
axs[1].imshow(sigma_minus_probs, cmap="viridis", origin="lower")
axs[1].set_title(r"$\sigma^-$ Emission Probabilities")
axs[1].set_xlabel("Light Hole State (n_hl)")
axs[1].set_ylabel("Heavy Hole State (n_hh)")
plt.colorbar(axs[1].imshow(sigma_minus_probs, cmap="viridis", origin="lower"), ax=axs[1])

# Plot Difference in Emission
axs[2].imshow(sigma_difference, cmap="coolwarm", origin="lower")
axs[2].set_title(r"Difference: $\sigma^+ - \sigma^-$")
axs[2].set_xlabel("Light Hole State (n_hl)")
axs[2].set_ylabel("Heavy Hole State (n_hh)")
plt.colorbar(axs[2].imshow(sigma_difference, cmap="coolwarm", origin="lower"), ax=axs[2])

# Plot Overall Dominant Emission Probability
axs[3].imshow(overall_dominant_emission, cmap="plasma", origin="lower")
axs[3].set_title("Overall Dominant Emission")
axs[3].set_xlabel("Light Hole State (n_hl)")
axs[3].set_ylabel("Heavy Hole State (n_hh)")
plt.colorbar(axs[3].imshow(overall_dominant_emission, cmap="plasma", origin="lower"), ax=axs[3])

plt.tight_layout()
plt.show()
