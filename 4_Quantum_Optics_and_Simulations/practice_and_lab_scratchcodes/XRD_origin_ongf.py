import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks  # Import the find_peaks function

# Define the filename for your XRD data
filename = "lncd1.txt"

# Load the XRD data from the text file (assuming it's a simple space-separated file)
data = np.loadtxt(filename)

# Assuming the data has two columns: 2Theta (X-axis) and Intensity (Y-axis)
xrd_x = data[:, 0]  # 2Theta values
xrd_y = data[:, 1]  # Intensity values

# Create a plot
plt.figure(figsize=(8, 6))
plt.plot(xrd_x, xrd_y, label="XRD Data")
plt.xlabel("2Theta (degrees)")
plt.ylabel("Intensity")
plt.title("X-ray Diffraction (XRD) Data")
plt.legend()
plt.grid(True)

# Find peaks in the XRD data using a threshold (you can adjust the threshold as needed)
threshold = 0.1  # Adjust this threshold based on your data
peaks, _ = find_peaks(xrd_y, height=threshold)

particle_sizes = []  # To store particle sizes for all peaks

# Loop through each peak and calculate the particle size and lattice constant
for peak_index in peaks:
    peak_2theta = xrd_x[peak_index]
    peak_intensity = xrd_y[peak_index]

    # Calculate the FWHM (Full Width at Half Maximum) of the peak
    half_max = peak_intensity / 2
    left_index = np.argmin(np.abs(xrd_y[:peak_index] - half_max))
    right_index = np.argmin(np.abs(xrd_y[peak_index:] - half_max)) + peak_index
    fwhm = xrd_x[right_index] - xrd_x[left_index]

    # Calculate the particle size and lattice constant using the Scherrer equation
    # Assuming wavelength of X-ray source (λ) and a shape factor (K) specific to the crystalline material
    wavelength = 1.54056  # Example wavelength for Cu Kα1 radiation (in Ångstroms)
    K = 0.94  # Example shape factor for spherical particles (for other shapes, use different K values)

    particle_size = (K * wavelength) / (fwhm * np.cos(np.radians(peak_2theta)))
    lattice_constant = wavelength / (2 * np.sin(np.radians(peak_2theta / 2)))

    particle_sizes.append(particle_size)

    # Print peak information
    print(f"Peak at 2Theta={peak_2theta}, FWHM={fwhm}")
    print(f"Estimated Particle Size: {particle_size:.2f} Å")
    print(f"Estimated Lattice Constant: {lattice_constant:.2f} Å")
    print("-" * 30)

# Calculate the average particle size
average_particle_size = np.mean(particle_sizes)

# Annotate the graph with the average particle size
plt.annotate(f'Average Particle Size: {average_particle_size:.2f} Å',
             xy=(0.5, 0.9), xycoords='axes fraction',
             fontsize=12, ha='center', color='red')

# Show the plot
plt.show()
