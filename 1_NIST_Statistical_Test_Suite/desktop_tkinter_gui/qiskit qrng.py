from qiskit import QuantumCircuit, Aer, transpile, assemble
from qiskit.visualization import plot_histogram
import numpy as np

def quantum_random_number_generator(bit_count):
    # Create a quantum circuit with 'bit_count' qubits
    circuit = QuantumCircuit(bit_count, bit_count)

    # Apply Hadamard gate to each qubit
    circuit.h(range(bit_count))

    # Measure qubits
    circuit.measure(range(bit_count), range(bit_count))

    # Use Aer's qasm_simulator
    simulator = Aer.get_backend('qasm_simulator')

    # Compile and run the Quantum circuit on the simulator
    compiled_circuit = transpile(circuit, simulator)
    result = simulator.run(assemble(compiled_circuit)).result()

    # Get the counts from the result
    counts = result.get_counts(circuit)

    # Convert counts to a binary string
    binary_string = max(counts, key=counts.get)

    # Convert binary string to decimal
    decimal_number = int(binary_string, 2)

    return decimal_number

def generate_and_save_random_numbers(file_path, num_numbers, bit_count):
    # Generate random numbers using QRNG and convert them to binary format
    random_numbers_binary = [format(quantum_random_number_generator(bit_count), f'0{bit_count}b') for _ in range(num_numbers)]

    # Save random numbers to a text file
    with open(file_path, 'w') as file:
        for num_binary in random_numbers_binary:
            file.write(f"{num_binary}")

if __name__ == "__main__":
    # Set the parameters
    file_path = "zzrandom_numbers_binary.txt"
    num_numbers = 100000
    bit_count = 10

    # Generate and save random numbers in binary format
    generate_and_save_random_numbers(file_path, num_numbers, bit_count)
    print(f"Random numbers (binary format) saved to {file_path}")
