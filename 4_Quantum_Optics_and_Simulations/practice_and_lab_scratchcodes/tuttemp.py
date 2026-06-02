from qiskit import QuantumCircuit, transpile, assemble
from qiskit_aer import Aer
from qiskit.primitives import Sampler
import numpy as np

# Parameters
L = 1.0  # Length of the box
m = 1.0  # Mass of the particle
hbar = 1.0  # Reduced Planck's constant
n = 2  # Number of qubits to simulate

# Energy levels
def energy_level(n, L, m, hbar):
    return (n**2 * np.pi**2 * hbar**2) / (2 * m * L**2)

# Quantum circuit
def create_circuit(n):
    qc = QuantumCircuit(n)
    qc.h(range(n))  # Apply Hadamard gates
    return qc

# Create and simulate the circuit
def simulate_circuit(n):
    qc = create_circuit(n)
    transpiled_circuit = transpile(qc, optimization_level=3)  # Transpile the circuit
    qobj = assemble(transpiled_circuit)  # Assemble the circuit into a Qobj
    simulator = Aer.get_backend('aer_simulator')  # Get the simulator backend
    sampler = Sampler(simulator)  # Correct creation of sampler
    result = sampler.run(transpiled_circuit).result()  # Run the circuit and get the result
    statevector = result.get_statevector(transpiled_circuit)  # Get the statevector
    return statevector

# Display energy levels
for level in range(1, n + 1):
    E = energy_level(level, L, m, hbar)
    print(f"Energy level {level}: E_{level} = {E}")

# Simulate and display the quantum circuit
statevector = simulate_circuit(n)
print(f"Quantum statevector:\n{statevector}")
