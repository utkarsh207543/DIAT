import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0  # Reduced Planck's constant
m = 1.0     # Mass of the particle
omega = 1.0 # Angular frequency of the oscillator

# Define the potential energy function for the harmonic oscillator
def potential_energy(x):
    return 0.5 * m * omega**2 * x**2

# Discretize the spatial domain
x_min = -5.0
x_max = 5.0
num_points = 500
x = np.linspace(x_min, x_max, num_points)

# Construct the Hamiltonian matrix
dx = x[1] - x[0]
H = np.zeros((num_points, num_points))
for i in range(num_points):
    H[i, i] = 1 / (dx**2) + potential_energy(x[i])
    if i > 0:
        H[i, i - 1] = -0.5 / (dx**2)
    if i < num_points - 1:
        H[i, i + 1] = -0.5 / (dx**2)

# Solve the eigenvalue problem
eigenvalues, eigenvectors = np.linalg.eigh(H)

# Plot the probability density for the first few energy levels
num_levels_to_plot = 5
plt.figure(figsize=(8, 6))
for level in range(num_levels_to_plot):
    probability_density = eigenvectors[:, level] ** 2
    plt.plot(x, probability_density, label=f'Level {level}')

plt.title('Probability Density for Harmonic Oscillator')
plt.xlabel('Position (x)')
plt.ylabel('Probability Density')
plt.legend()
plt.grid()
plt.show()
