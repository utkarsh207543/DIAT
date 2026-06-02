import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
from qiskit_aer import AerSimulator

# -----------------------------
# Helper: PMD element
# -----------------------------
def PMD_channel(delta_phi, theta):
    """
    delta_phi : differential phase delay (PMD strength)
    theta     : random birefringence angle
    """
    qc = QuantumCircuit(1)

    # Random birefringence (polarization rotation)
    qc.ry(2 * theta, 0)

    # Differential group delay (relative phase)
    qc.rz(delta_phi, 0)

    # Rotate back
    qc.ry(-2 * theta, 0)

    return qc

# -----------------------------
# Initial polarization state |D> = (|H> + |V>)/sqrt(2)
# -----------------------------
qc_init = QuantumCircuit(1)
qc_init.h(0)  # |+> polarization

psi_ideal = Statevector.from_instruction(qc_init)

# -----------------------------
# PMD sweep
# -----------------------------
delta_phi_values = np.linspace(0, np.pi, 40)
num_realizations = 200

purity = []
fidelity = []

for delta_phi in delta_phi_values:
    rho_avg = DensityMatrix(np.zeros((2, 2)))

    for _ in range(num_realizations):
        theta = np.random.uniform(0, np.pi)

        qc = QuantumCircuit(1)
        qc.compose(qc_init, inplace=True)
        qc.compose(PMD_channel(delta_phi, theta), inplace=True)

        psi = Statevector.from_instruction(qc)
        rho_avg += DensityMatrix(psi)

    rho_avg /= num_realizations

    # Purity Tr(rho^2)
    purity.append(np.real(np.trace(rho_avg.data @ rho_avg.data)))

    # Fidelity with ideal state
    fidelity.append(state_fidelity(rho_avg, psi_ideal))

# -----------------------------
# Plot results
# -----------------------------
plt.figure(figsize=(6,4))
plt.plot(delta_phi_values, purity, label="Purity")
plt.plot(delta_phi_values, fidelity, label="Fidelity")
plt.xlabel("Differential Phase Delay Δφ (PMD strength)")
plt.ylabel("Metric value")
plt.title("Polarization Mode Dispersion via Quantum Circuits")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
