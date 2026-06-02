import os
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from datetime import datetime
import cupy as cp  # Optional for GPU-based post-processing

# ---------- CONFIGURATION ----------
NUM_QUBITS = 16
BATCH_SIZE = 1024  # Number of circuits per batch
FILENAME = f"QRNG_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
FILE_SIZE_THRESHOLD_KB = 500 * 1024  # 500 KB in Bytes


# ----------------------------------


def generate_random_batch(num_qubits, batch_size, simulator):
    """Generates a batch of random binary strings using GPU-enabled Qiskit Aer."""
    circuit = QuantumCircuit(num_qubits, num_qubits)
    for qubit in range(num_qubits):
        circuit.h(qubit)
    circuit.measure(range(num_qubits), range(num_qubits))

    compiled = transpile(circuit, simulator)
    job = simulator.run(compiled, shots=batch_size)
    result = job.result()
    counts = result.get_counts()

    binaries = []
    for bitstring, count in counts.items():
        binaries.extend([bitstring] * count)
    return binaries


def write_batch_to_file(num_qubits, batch_size, filename, simulator):
    """Generates a batch of random numbers and appends to file."""
    binary_numbers = generate_random_batch(num_qubits, batch_size, simulator)
    with open(filename, 'a') as f:
        for binary in binary_numbers:
            f.write(binary)
    file_size_kb = os.path.getsize(filename) / 1024
    print(f"[INFO] Written {len(binary_numbers)} binaries. Current file size: {file_size_kb:.2f} KB")


def check_file_size(file_path, threshold_bytes):
    """Checks if the file has reached the threshold size."""
    return os.path.exists(file_path) and os.path.getsize(file_path) >= threshold_bytes


def load_binary_to_gpu(filename):
    """Loads binary file to CuPy array for GPU post-processing (optional)."""
    with open(filename, 'r') as f:
        data = f.read().strip()
    return cp.array(list(data), dtype=cp.uint8)


if __name__ == "__main__":
    # Initialize GPU simulator
    simulator = AerSimulator(method='statevector', device='GPU')

    print(f"[INFO] Starting QRNG generation with {NUM_QUBITS} qubits per sample...")
    while True:
        write_batch_to_file(NUM_QUBITS, BATCH_SIZE, FILENAME, simulator)
        if check_file_size(FILENAME, FILE_SIZE_THRESHOLD_KB):
            print(f"[DONE] File size reached {FILE_SIZE_THRESHOLD_KB / 1024:.2f} KB. Stopping.")
            break

    # Optional: Uncomment below to load generated binary file to GPU for further processing
    # print("[INFO] Loading data to GPU for post-processing...")
    # gpu_data = load_binary_to_gpu(FILENAME)
    # print(f"[INFO] Loaded {gpu_data.size} bits to GPU.")
