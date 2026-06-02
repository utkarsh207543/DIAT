import os
import time
from datetime import datetime
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from tqdm import tqdm  # for progress bar

def generate_random_binary(num_qubits):
    circuit = QuantumCircuit(num_qubits, num_qubits)
    for qubit in range(num_qubits):
        circuit.h(qubit)
    circuit.measure(range(num_qubits), range(num_qubits))

    simulator = AerSimulator()
    compiled_circuit = transpile(circuit, simulator)
    job = simulator.run(compiled_circuit, shots=1)
    result = job.result()
    counts = result.get_counts()
    return list(counts.keys())[0]

def write_random_data_until_size(num_qubits, target_bytes, filename):
    with open(filename, 'a') as file:
        print(f"\nGenerating {target_bytes / (1024 * 1024):.2f} MB of quantum random data...")
        start_time = time.time()
        pbar = tqdm(total=target_bytes, unit='B', unit_scale=True)

        total_written = 0
        while total_written < target_bytes:
            binary_number = generate_random_binary(num_qubits)
            file.write(binary_number)
            total_written += len(binary_number)
            pbar.update(len(binary_number))

        pbar.close()
        elapsed = time.time() - start_time
        print(f"✅ Done! Total size: {total_written / (1024 * 1024):.2f} MB")
        print(f"⏱️ Elapsed time: {elapsed:.2f} seconds")

def main():
    try:
        mb_size = float(input("Required Output File Size (in MB): "))
    except ValueError:
        print("❌ Invalid input. Please enter a numeric value.")
        return

    target_bytes = int(mb_size * 1024 * 1024)
    num_qubits = 4  # Each shot gives 8 bits

    filename = f"QRNG_2_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    write_random_data_until_size(num_qubits, target_bytes, filename)

if __name__ == "__main__":
    main()
