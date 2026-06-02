import numpy as np
import matplotlib.pyplot as plt

# Constants
theta = np.linspace(0, 2 * np.pi, 1000)  # Angle of polarization
amplitude = np.cos(theta)  # Amplitude of light wave, polarized along theta

# Create a polarizer filter
polarizer_angle = np.pi / 2 # Angle of the polarizer
polarizer_transmittance = np.cos(theta - polarizer_angle)**2  # Transmittance through the polarizer

# Simulate the effect of the polarizer
polarized_light = amplitude * polarizer_transmittance

# Plot the original and polarized light
plt.figure(figsize=(8, 6))
plt.plot(theta, amplitude, label='Original Light')
plt.plot(theta, polarized_light, label='Polarized Light')
plt.xlabel('Angle (radians)')
plt.ylabel('Amplitude')
plt.title('Simulation of Polarized Light')
plt.legend()
plt.grid(True)
plt.show()
