from qiskit import QuantumCircuit, Aer, transpile, execute
import numpy as np

# Number of random numbers to generate
num_random_numbers = 2058

# Create a quantum circuit
qrng_circuit = QuantumCircuit(5, 5)

# Apply the Hadamard gate to each qubit
for i in range(5):
    qrng_circuit.h(i)

# Measure all qubits
qrng_circuit.measure(range(5), range(5))

# Choose the backend for simulation
backend = Aer.get_backend('qasm_simulator')

# Compile the circuit
compiled_circuit = transpile(qrng_circuit, backend)

# Initialize an empty list to store random numbers
random_numbers = []

# Generate random numbers and store them
for _ in range(num_random_numbers):
    result = execute(compiled_circuit, backend, shots=1).result()
    counts = result.get_counts()
    random_number_binary = list(counts.keys())[0]
    random_number_decimal = int(random_number_binary, 2)
    random_numbers.append(random_number_decimal)

# Save random numbers to a file
with open('random_numbers.txt', 'w') as file:
    for number in random_numbers:
        file.write(str(number) + '\n')

print(f"{num_random_numbers} random numbers generated and saved to 'random_numbers.txt'.")
