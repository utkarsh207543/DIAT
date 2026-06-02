import os
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit import transpile
from datetime import datetime

def generate_random_binary(num_qubits):
    # Create a Quantum Circuit acting on a quantum register of num_qubits
    circuit = QuantumCircuit(num_qubits, num_qubits)

    # Apply a Hadamard gate to each qubit
    for qubit in range(num_qubits):
        circuit.h(qubit)

    # Measure the qubits
    circuit.measure(range(num_qubits), range(num_qubits))

    # Use Aer's simulator
    simulator = AerSimulator()

    # Manually define coupling map for at least 64 qubits
    coupling_map = [[i, j] for i in range(num_qubits) for j in range(i+1, num_qubits)]

    # Transpile the circuit for the simulator with custom coupling map
    compiled_circuit = transpile(circuit, simulator, coupling_map=coupling_map)

    # Execute the circuit on the simulator
    job = simulator.run(compiled_circuit, shots=1)

    # Get the results
    result = job.result()
    counts = result.get_counts()

    # Extract the binary random number from the counts
    random_binary = list(counts.keys())[0]
    return random_binary

def write_random_numbers_to_file(num_qubits, num_numbers, filename):
    # Limit the number of numbers to avoid overwhelming resources
    max_safe_numbers = 10**7  # 10 million is more practical
    if num_numbers > max_safe_numbers:
        raise ValueError(f"Too many numbers requested. Limit to {max_safe_numbers}.")

    # Open the file once in append mode
    with open(filename, 'a') as file:
        print(f"Generating {num_numbers} random binary numbers...")

        for _ in range(num_numbers):
            binary_number = generate_random_binary(num_qubits)
            file.write(binary_number)

    # Calculate and display file size after saving
    file_size = os.path.getsize(filename) / 1024  # File size in KB
    print(f"Generated {num_numbers}/{num_numbers} numbers. Final file size: {file_size:.2f} KB")

# Parameters
num_qubits = 2  # Number of qubits
num_numbers = 1024  # Number of random numbers to generate (adjusted for practicality)
filename = f"QRNG_1_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt" # Output file

# Initialize threshold value for 500 KB in bytes
threshold_kb = 1 * 1024 * 1024 * 1025

# Function to check file size
def check_file_size(file_path, threshold):
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        return file_size >= threshold
    return False

# Path to the file to monitor
file_path = filename  # Use the filename as the path

# Main loop
while True:
    # Generate and save random numbers
    write_random_numbers_to_file(num_qubits, num_numbers, filename)
    if check_file_size(file_path, threshold_kb):
        print(f"File size has reached {threshold_kb / 1024} KB. Exiting program.")
        break
