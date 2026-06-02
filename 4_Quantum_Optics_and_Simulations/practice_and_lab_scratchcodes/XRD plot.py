import numpy as np
import matplotlib.pyplot as plt

filename = "lncd1.txt" #XRD file


data = np.loadtxt(filename)

#File to arrays
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

# Show the plot
plt.show()