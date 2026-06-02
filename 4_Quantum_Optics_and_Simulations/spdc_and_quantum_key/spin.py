import matplotlib.pyplot as plt
import numpy as np

# Define the quantum numbers and corresponding energies for AlGaAs quantum well
states = ["E1", "HH1", "LH1"]  # Electron (E1), Heavy hole (HH1), Light hole (LH1) states
m_j_values = ["±1/2", "±3/2", "±1/2"]
energies = [100, 50, 30]  # Arbitrary energy levels in meV, conduction band on top, valence bands below

# Define radiative transitions
transitions = [
    (0, 1, "σ⁺"),  # E1 to HH1 with σ⁺ polarization
    (0, 2, "σ⁻"),  # E1 to LH1 with σ⁻ polarization
]

# Define transition probability density matrix (arbitrary values for demonstration)
# Rows represent the initial state, columns represent the final state
probability_density_matrix = np.array([
    [0.0, 0.8, 0.6],  # E1
    [0.0, 0.0, 0.0],  # HH1
    [0.0, 0.0, 0.0],  # LH1
])

# Calculate total transition probabilities for TM and TE modes
# Assuming TM corresponds to σ⁺ and TE corresponds to σ⁻
probabilities_TM = probability_density_matrix[0, 1]  # E1 to HH1 (σ⁺)
probabilities_TE = probability_density_matrix[0, 2]  # E1 to LH1 (σ⁻)
ratio_TM_TE = probabilities_TM / probabilities_TE

# Print the ratio of TM to TE probabilities
print(f"Probability TM: {probabilities_TM}")
print(f"Probability TE: {probabilities_TE}")
print(f"TM/TE Ratio: {ratio_TM_TE}")

# Plot energy levels
fig, ax = plt.subplots(figsize=(8, 6))
for i, (state, m_j, energy) in enumerate(zip(states, m_j_values, energies)):
    ax.hlines(y=energy, xmin=0, xmax=1, color="blue", label="" if i else "Energy Levels")
    ax.text(1.1, energy, f"{state} ({m_j})", fontsize=10, verticalalignment="center")

# Plot transitions
colors = {"σ⁺": "red", "σ⁻": "green"}
offset = 0.1  # Offset to separate the lines
for i, (start, end, polarization) in enumerate(transitions):
    x_start, x_end = 0.5 + (i * offset), 0.5 + (i * offset)
    y_start, y_end = energies[start], energies[end]
    ax.annotate(
        "",
        xy=(x_end, y_end),
        xytext=(x_start, y_start),
        arrowprops=dict(arrowstyle="->", color=colors[polarization], lw=2),
    )
    ax.text(
        x_end + 0.1,
        (y_start + y_end) / 2,
        polarization,
        color=colors[polarization],
        fontsize=12,
        verticalalignment="center",
    )

# Add vertical geometry illustration
ax.axvline(x=0.5, ymin=0.1, ymax=0.9, color="gray", linestyle="--", label="Vertical Geometry")

# Formatting the plot
ax.set_xlim(-0.5, 2)
ax.set_ylim(0, 120)
ax.set_xlabel("Quantum Well Structure", fontsize=12)
ax.set_ylabel("Energy (meV)", fontsize=12)
ax.set_title("Radiative Transitions in AlGaAs Quantum Well Laser", fontsize=14)
ax.legend(loc="upper right")
ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()
