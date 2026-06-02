import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, state_fidelity, random_unitary, Statevector
from qiskit.circuit.library import RZGate


def simulate_pmd_improved(n_steps=20, n_realizations=500):
    """
    Simulates PMD using a Single-Qubit Quantum Circuit with Haar-Random Birefringence.

    Parameters:
    - n_steps: Number of delta_phi points to simulate (x-axis resolution).
    - n_realizations: Number of random fibers to average over per point (ensemble size).
    """

    # 1. Define the range of Differential Phase Delay (Delta Phi)
    # We sweep from 0 to pi (half a wave cycle)
    delta_phi_range = np.linspace(0, np.pi, n_steps)

    purity_results = []
    fidelity_results = []

    # Define Input State |D> = (|H> + |V>) / sqrt(2)
    # In Qiskit, |0> is usually H. We apply Hadamard to get |+> (Diagonal)
    qc_prep = QuantumCircuit(1)
    qc_prep.h(0)
    input_state = Statevector.from_instruction(qc_prep)

    print(f"Starting Simulation over {n_steps} steps with {n_realizations} realizations each...")

    for d_phi in delta_phi_range:

        # Initialize an empty density matrix to accumulate the ensemble average
        # Start with a zero matrix
        rho_ensemble = np.zeros((2, 2), dtype=complex)

        for _ in range(n_realizations):
            # --- The Physics Improvement ---
            # Instead of R_y(theta), we use a General Random Unitary (Haar Random).
            # This models random birefringence covering the full Poincare sphere.
            U_birefringence = random_unitary(2)

            # Create the PMD Circuit: U_eff = U_BR^dagger * Rz(phi) * U_BR
            # This rotates to the fiber's principal axes, applies delay, and rotates back.
            qc = QuantumCircuit(1)

            # 1. Rotate to Fiber Eigenaxes (Random)
            qc.append(U_birefringence.to_instruction(), [0])

            # 2. Apply Differential Phase Delay (PMD)
            qc.append(RZGate(d_phi), [0])

            # 3. Rotate back to Lab Frame (Inverse of Step 1)
            qc.append(U_birefringence.adjoint().to_instruction(), [0])

            # Execute circuit conceptually to get the final state vector
            # (In ideal simulation, we don't need 'shots', we can just calculate the vector)
            final_vec = input_state.evolve(qc)

            # Add to ensemble density matrix: rho = |psi><psi|
            rho_current = final_vec.to_operator().data
            rho_ensemble += rho_current

        # Normalize the average density matrix
        rho_final = DensityMatrix(rho_ensemble / n_realizations)

        # --- Calculate Metrics ---
        # 1. Purity = Tr(rho^2)
        purity = rho_final.purity().real

        # 2. Fidelity = <D| rho |D>
        fid = state_fidelity(input_state, rho_final)

        purity_results.append(purity)
        fidelity_results.append(fid)

    return delta_phi_range, purity_results, fidelity_results


# --- Run the Simulation ---
d_phi, purities, fidelities = simulate_pmd_improved(n_steps=30, n_realizations=300)

# --- Plotting (Matches your Optica style) ---
plt.figure(figsize=(7, 5), dpi=120)
plt.plot(d_phi, purities, label='Purity (State Coherence)', linewidth=2)
plt.plot(d_phi, fidelities, label='Fidelity (w.r.t Input)', linewidth=2, linestyle='--')

plt.title('Simulated PMD: Random Unitary Model (3D Birefringence)', fontsize=12)
plt.xlabel(r'Differential Phase Delay $\Delta\phi$ (rad)', fontsize=11)
plt.ylabel('Metric Value', fontsize=11)
plt.ylim(0.45, 1.05)
plt.legend(fontsize=10)
plt.grid(True, linestyle='--', alpha=0.7)

# Theoretical limit line for fully mixed state
plt.axhline(0.5, color='gray', linestyle=':', alpha=0.5, label='Fully Mixed Limit')

plt.tight_layout()
plt.show()