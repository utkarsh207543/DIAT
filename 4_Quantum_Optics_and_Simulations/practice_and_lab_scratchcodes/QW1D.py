import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eig

# Constants
h_bar = 1.0545718e-34  # Reduced Planck's constant (Joule second)
m = 9.10938356e-31     # Electron mass (kg)
L = 1e-10              # Width of the well (meters)
V0 = 1e-18             # Potential barrier height (Joules)

# Number of states to calculate
num_states = 3

# Discretization parameters
num_points = 1000
x_values = np.linspace(0, L, num_points)
dx = x_values[1] - x_values[0]

# Potential energy function (square well potential)
def potential_energy(x):
    return np.where(x < L / 2, 0, V0)

# Kinetic energy operator matrix
T = np.diag(-2 * np.ones(num_points)) + np.diag(np.ones(num_points - 1), k=1) + np.diag(np.ones(num_points - 1), k=-1)
T /= dx**2

# Potential energy operator matrix
V = np.diag(potential_energy(x_values))

# Hamiltonian matrix
H = -(h_bar**2 / (2 * m)) * T + V

# Solve for eigenstates and eigenenergies
eigenvalues, eigenvectors = eig(H)

# Sort eigenvalues and corresponding eigenvectors
sorted_indices = np.argsort(eigenvalues)
eigenvalues = eigenvalues[sorted_indices]
eigenvectors = eigenvectors[:, sorted_indices]

# Create subplots
fig, axs = plt.subplots(num_states + 1, 1, figsize=(8, 2 * (num_states + 1)))

# Plot the potential energy
axs[0].plot(x_values, potential_energy(x_values), label='Potential Energy')
axs[0].set_title('Potential Energy')
axs[0].set_xlabel('Position (meters)')
axs[0].set_ylabel('Energy (Joules)')
axs[0].legend()

# Plot each eigenstate separately
for i in range(num_states):
    eigenstate = eigenvectors[:, i]
    eigenstate /= np.max(np.abs(eigenstate))  # Normalize for better visualization
    axs[i + 1].plot(x_values, eigenstate + eigenvalues[i], label=f'n={i+1} state')
    axs[i + 1].set_title(f'n={i+1} State')
    axs[i + 1].set_xlabel('Position (meters)')
    axs[i + 1].set_ylabel('Energy (Joules)')
    axs[i + 1].legend()

plt.tight_layout()
plt.show()
