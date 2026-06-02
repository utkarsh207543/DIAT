import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, state_fidelity, Statevector
from qiskit.circuit.library import RYGate, RZGate


def simulate_pmd_linear_model(n_steps=30, n_realizations=200):
    # 1. Sweep Delta Phi from 0 to pi
    delta_phi_range = np.linspace(0, np.pi, n_steps)
    purity_results = []
    fidelity_results = []

    # Input State |D>
    qc_prep = QuantumCircuit(1)
    qc_prep.h(0)
    input_state = Statevector.from_instruction(qc_prep)

    for d_phi in delta_phi_range:
        rho_ensemble = np.zeros((2, 2), dtype=complex)

        for _ in range(n_realizations):
            # Matches Eq 2: Uniform theta in [0, pi]
            theta = np.random.uniform(0, np.pi)

            # Circuit: U_eff = U_BR^dagger * Rz * U_BR
            # Note: U_BR = Ry(2*theta)
            qc = QuantumCircuit(1)
            qc.ry(2 * theta, 0)  # U_BR
            qc.rz(d_phi, 0)  # PMD
            qc.ry(-2 * theta, 0)  # U_BR dagger

            final_vec = input_state.evolve(qc)
            rho_ensemble += final_vec.to_operator().data

        rho_final = DensityMatrix(rho_ensemble / n_realizations)
        purity_results.append(rho_final.purity().real)
        fidelity_results.append(state_fidelity(input_state, rho_final))

    return delta_phi_range, purity_results, fidelity_results


# Generate and Save
d_phi, pur, fid = simulate_pmd_linear_model()

plt.figure(figsize=(6, 4), dpi=300)
plt.plot(d_phi, pur, label='Purity $\mathcal{P}$', linewidth=2)
plt.plot(d_phi, fid, label='Fidelity $\mathcal{F}$', linewidth=2, linestyle='--')
plt.xlabel(r'Differential Phase Delay $\Delta\phi$ (rad)')
plt.ylabel('Metric Value')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig('Figure_1.png')  # This saves the file for your LaTeX
plt.show()