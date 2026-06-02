import numpy as np
import matplotlib.pyplot as plt

# Constants
hbar = 1.0  # reduced Planck constant
m = 1.0    # mass of the particle
omega = 1.0  # angular frequency of the harmonic oscillator potential

# Function to calculate the action
def calculate_action(x, delta_t):
    kinetic_term = 0.5 * m * ((np.roll(x, -1) - x) / delta_t)**2
    potential_term = 0.5 * m * omega**2 * x**2
    return np.sum(kinetic_term - potential_term) * delta_t / hbar

# Function to perform path integral using Trotter formula
def path_integral(x_initial, x_final, num_steps, total_time):
    delta_t = total_time / num_steps
    paths = np.zeros((num_steps + 1, len(x_initial)), dtype=complex)
    paths[0, :] = x_initial

    for step in range(1, num_steps + 1):
        action = calculate_action(paths[step - 1, :], delta_t)
        exponent = np.exp(-1j * action / hbar)
        paths[step, :] = paths[step - 1, :] * exponent

    return paths

# Parameters
num_steps = 500
total_time = 5.0
x_initial = np.linspace(-5, 5, num_steps)
x_final = np.linspace(-5, 5, num_steps)

# Perform path integral
paths = path_integral(x_initial, x_final, num_steps, total_time)

# Plot the results
plt.figure(figsize=(12, 8))

# Plot probability density functions for n=1 to n=5
for n in range(1, 6):
    state = np.abs(paths[n - 1, :])**2
    plt.subplot(5, 2, 2 * n - 1)
    plt.plot(x_initial, state, label=f'State {n}')
    plt.title(f'Probability Density for State {n}')
    plt.xlabel('Position (x)')
    plt.ylabel('|ψ(x)|²')
    plt.legend()

    plt.subplot(5, 2, 2 * n)
    plt.plot(np.real(paths[n - 1, :]), np.imag(paths[n - 1, :]), label=f'State {n}')
    plt.title(f'Trajectory in Complex Plane for State {n}')
    plt.xlabel('Re(x)')
    plt.ylabel('Im(x)')
    plt.legend()

plt.tight_layout()
plt.show()
