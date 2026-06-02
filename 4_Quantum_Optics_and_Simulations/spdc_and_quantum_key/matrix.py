import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0545718e-34  # Reduced Planck's constant (Joule*seconds)
m_e = 9.10938356e-31  # Mass of electron (kg)
eV = 1.60218e-19      # Electron volt (Joules)

# Quantum well parameters
L = 1e-9  # Width of the quantum well (meters)

# Number of states to calculate
num_states = 5

# Calculate energy levels (in Joules)
def energy_level(n, L, m):
    return (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2)

# Calculate wavefunction
# Returns the wavefunction \psi_n(x) for state n at position x
def wavefunction(n, x, L):
    return np.sqrt(2 / L) * np.sin(n * np.pi * x / L)

# Calculate the matrix element <n|x|m> for position operator x
def position_matrix_element(n, m, L):
    if (n + m) % 2 == 0:  # Integral is zero when n+m is even
        return 0
    else:
        return (-2 * L / (np.pi**2) * (1 / (n**2 - m**2)))

# Calculate transition strength |<n|x|m>|^2
def transition_strength(n, m, L):
    element = position_matrix_element(n, m, L)
    return element**2

# Energy levels
energies = [energy_level(n, L, m_e) / eV for n in range(1, num_states + 1)]

# Calculate matrix elements and transition strengths
matrix_elements = np.zeros((num_states, num_states))
transition_strengths = np.zeros((num_states, num_states))

for n in range(1, num_states + 1):
    for m in range(1, num_states + 1):
        matrix_elements[n-1, m-1] = position_matrix_element(n, m, L)
        transition_strengths[n-1, m-1] = transition_strength(n, m, L)

# Print results
print("Energy Levels (eV):")
for i, energy in enumerate(energies):
    print(f"n={i+1}: {energy:.2f} eV")

print("\nMatrix Elements <n|x|m> (m):")
print(matrix_elements)

print("\nTransition Strengths |<n|x|m>|^2 (m^2):")
print(transition_strengths)

# Plot transition strengths
plt.figure(figsize=(8, 6))
plt.imshow(transition_strengths, cmap="viridis", origin="lower")
plt.colorbar(label="|<n|x|m>|^2 (m^2)")
plt.title("Transition Strengths |<n|x|m>|^2")
plt.xlabel("m")
plt.ylabel("n")
plt.xticks(range(num_states), range(1, num_states + 1))
plt.yticks(range(num_states), range(1, num_states + 1))
plt.show()
