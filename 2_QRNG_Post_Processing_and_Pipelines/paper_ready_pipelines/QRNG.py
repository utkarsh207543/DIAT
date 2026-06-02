import os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from datetime import datetime
from multiprocessing import Pool, cpu_count
from functools import partial

# Generate a single QRNG output
def generate_random_binary(num_qubits, _):
    circuit = QuantumCircuit(num_qubits, num_qubits)
    for qubit in range(num_qubits):
        circuit.h(qubit)
    circuit.measure(range(num_qubits), range(num_qubits))
    simulator = AerSimulator()
    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=1).result()
    return list(result.get_counts().keys())[0]

# Save to file
def save_to_file(filename, random_bits):
    with open(filename, 'a') as f:
        for bits in random_bits:
            f.write(bits)

# Check file size
def check_file_size(file_path, threshold):
    return os.path.exists(file_path) and os.path.getsize(file_path) >= threshold

# Entry point
if __name__ == '__main__':
    num_qubits = 2
    batch_size = 512
    filename = f"QRNG_CPU_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    threshold_kb = 1 * 1024 * 1024  # 1 MB
    file_path = filename

    while True:
        with Pool(cpu_count()) as pool:
            random_bits = pool.map(partial(generate_random_binary, num_qubits), range(batch_size))
        save_to_file(filename, random_bits)
        if check_file_size(file_path, threshold_kb):
            print(f"File size reached {(threshold_kb / 1024):.2f} KB. Exiting.")
            break
