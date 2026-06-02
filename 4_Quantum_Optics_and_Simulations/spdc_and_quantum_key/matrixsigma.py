import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0545718e-34  # Reduced Planck's constant (Joule*seconds)
m_e = 9.10938356e-31  # Mass of electron (kg)
m_hh = 0.5 * m_e      # Effective mass of heavy hole (kg)
m_hl = 0.25 * m_e     # Effective mass of light hole (kg)
eV = 1.60218e-19      # Electron volt (Joules)

# Quantum well parameters
L = 1e-9 # Width of the quantum well (meters)

# Number of states to calculate
num_states = 20

# Calculate energy levels (in Joules)
def energy_level(n, L, m):
    return (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2)

# Calculate wavefunction
# Returns the wavefunction \psi_n(x) for state n at position x
def wavefunction(n, x, L):
    return np.sqrt(2 / L) * np.sin(n * np.pi * x / L)

# Calculate the matrix element <HH|x|HL> for position operator x
def position_matrix_element_hh_hl(n_hh, n_hl, L):
    if (n_hh + n_hl) % 2 == 0:  # Integral is zero when n_hh + n_hl is even
        return 0
    else:
        return (-2 * L / (np.pi**2) * (1 / (n_hh**2 - n_hl**2)))

# Calculate emission probabilities for \u03c3+ and \u03c3-
def emission_probabilities(n_hh, n_hl, L):
    matrix_element = position_matrix_element_hh_hl(n_hh, n_hl, L)
    sigma_plus = matrix_element**2 / 2  # Simplified circular polarization term
    sigma_minus = matrix_element**2 / 2
    return sigma_plus, sigma_minus

# Energy levels
energies_hh = [energy_level(n, L, m_hh) / eV for n in range(1, num_states + 1)]
energies_hl = [energy_level(n, L, m_hl) / eV for n in range(1, num_states + 1)]

# Calculate matrix elements and emission probabilities
sigma_plus_probs = np.zeros((num_states, num_states))
sigma_minus_probs = np.zeros((num_states, num_states))

for n_hh in range(1, num_states + 1):
    for n_hl in range(1, num_states + 1):
        sigma_plus, sigma_minus = emission_probabilities(n_hh, n_hl, L)
        sigma_plus_probs[n_hh-1, n_hl-1] = sigma_plus
        sigma_minus_probs[n_hh-1, n_hl-1] = sigma_minus

# Calculate overall dominant emission probability
overall_dominant_emission = sigma_plus_probs + sigma_minus_probs

# Print results
print("Heavy Hole (HH) Energy Levels (eV):")
for i, energy in enumerate(energies_hh):
    print(f"n_hh={i+1}: {energy:.2f} eV")

print("\nLight Hole (HL) Energy Levels (eV):")
for i, energy in enumerate(energies_hl):
    print(f"n_hl={i+1}: {energy:.2f} eV")

print("\nσ+ Emission Probabilities:")
print(sigma_plus_probs)

print("\nσ- Emission Probabilities:")
print(sigma_minus_probs)

print("\nOverall Dominant Emission Probability:")
print(overall_dominant_emission)

# Determine which emission is more dominant
dominant_emission = np.argmax(overall_dominant_emission, axis=1)  # Get indices of max values for each row
dominant_emission_type = ['σ+' if x == 0 else 'σ-' for x in dominant_emission]  # σ+ for 0 and σ- for 1

print("\nDominant Emission for Each Pair (HH, HL):")
for i in range(num_states):
    print(f"Pair ({i+1}, {i+1}): {dominant_emission_type[i]}")

# Count occurrences of 'σ-' and 'σ+'
count_sigma_minus = dominant_emission_type.count('σ-')
count_sigma_plus = dominant_emission_type.count('σ+')
sigma_minus_count = count_sigma_minus
sigma_plus_count = count_sigma_plus

# Calculate probabilities
prob_sigma_minus = sigma_minus_count / (sigma_minus_count + sigma_plus_count)
prob_sigma_plus = sigma_plus_count / (sigma_minus_count + sigma_plus_count)

# Print probabilities
print(f"Probability σ-: {prob_sigma_minus:.2f}")
print(f"Probability σ+: {prob_sigma_plus:.2f}")

# Plot \u03c3+ and \u03c3- emission probabilities and overall dominant emission
plt.figure(figsize=(18, 6))

plt.subplot(1, 3, 1)
plt.imshow(sigma_plus_probs, cmap="viridis", origin="lower")
plt.colorbar(label="σ+ Probability")
plt.title("\u03c3+ Emission Probabilities")
plt.xlabel("Light Hole State (n_hl)")
plt.ylabel("Heavy Hole State (n_hh)")
plt.xticks(range(num_states), range(1, num_states + 1))
plt.yticks(range(num_states), range(1, num_states + 1))

plt.subplot(1, 3, 2)
plt.imshow(sigma_minus_probs, cmap="viridis", origin="lower")
plt.colorbar(label="σ- Probability")
plt.title("\u03c3- Emission Probabilities")
plt.xlabel("Light Hole State (n_hl)")
plt.ylabel("Heavy Hole State (n_hh)")
plt.xticks(range(num_states), range(1, num_states + 1))
plt.yticks(range(num_states), range(1, num_states + 1))

plt.subplot(1, 3, 3)
plt.imshow(overall_dominant_emission, cmap="viridis", origin="lower")
plt.colorbar(label="Overall Dominant Probability")
plt.title("Overall Dominant Emission Probability")
plt.xlabel("Light Hole State (n_hl)")
plt.ylabel("Heavy Hole State (n_hh)")
plt.xticks(range(num_states), range(1, num_states + 1))
plt.yticks(range(num_states), range(1, num_states + 1))

plt.tight_layout()
plt.show()





