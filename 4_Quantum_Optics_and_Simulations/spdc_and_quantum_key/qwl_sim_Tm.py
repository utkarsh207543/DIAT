import numpy as np
import matplotlib.pyplot as plt

# Constants
N_transitions = 10000  # Number of spontaneous emission events
TE_ratio = 0.7  # TE-polarized emission probability
TM_ratio = 0.3  # TM-polarized emission probability (adjustable)

# Random photon emission simulation
np.random.seed(42)  # For reproducibility
emission_types = np.random.choice(['TE', 'TM'], size=N_transitions, p=[TE_ratio, TM_ratio])

# Count occurrences
TE_count = np.sum(emission_types == 'TE')
TM_count = np.sum(emission_types == 'TM')

# Visualization: Histogram of photon emission types
plt.figure(figsize=(8, 5))
plt.bar(['TE', 'TM'], [TE_count, TM_count], color=['blue', 'red'], alpha=0.7)
plt.title("Photon Emission Distribution in Quantum Well Laser")
plt.ylabel("Number of Photons")
plt.xlabel("Polarization Type")
plt.text(0, TE_count, f"{TE_count} TE", ha='center', va='bottom', fontsize=12, color='blue')
plt.text(1, TM_count, f"{TM_count} TM", ha='center', va='bottom', fontsize=12, color='red')
plt.grid(axis='y')
plt.show()

# Print results
print(f"Total TE-Polarized Photons: {TE_count}")
print(f"Total TM-Polarized Photons: {TM_count}")
print(f"TM Emission Probability: {TM_count / N_transitions:.2f}")
