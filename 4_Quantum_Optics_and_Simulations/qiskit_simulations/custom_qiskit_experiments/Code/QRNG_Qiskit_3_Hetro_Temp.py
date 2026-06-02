import os
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from tqdm import tqdm

def generate_random_batch(args):
    num_qubits, shots = args
    circuit = QuantumCircuit(num_qubits, num_qubits)
    circuit.h(range(num_qubits))
    circuit.measure(range(num_qubits), range(num_qubits))

    simulator = AerSimulator()
    transpiled_circuit = transpile(circuit, simulator)
    job = simulator.run(transpiled_circuit, shots=shots)
    result = job.result()
    counts = result.get_counts()

    # Flatten all outcomes into one long bitstring
    bitstring = ''
    for outcome, count in counts.items():
        bitstring += outcome * count
    return bitstring[::-1]  # reverse because Qiskit returns bits least-significant first

def write_parallel_random_data(num_qubits, target_bytes, filename, shots_per_batch=1000):
    start_time = time.time()
    batch_bits = num_qubits * shots_per_batch
    batch_bytes = batch_bits // 8

    n_processes = max(1, cpu_count() - 1)
    pool = Pool(processes=n_processes)

    with open(filename, 'w') as file:
        print(f"\n🧠 Using {n_processes} processes with {shots_per_batch} shots per batch.")
        print(f"📦 Target: {target_bytes / (1024*1024):.2f} MB\n")

        total_written = 0
        pbar = tqdm(total=target_bytes, unit='B', unit_scale=True)

        while total_written < target_bytes:
            batches_needed = max(1, (target_bytes - total_written) // batch_bytes)
            args_list = [(num_qubits, shots_per_batch)] * batches_needed

            for result in pool.imap_unordered(generate_random_batch, args_list):
                file.write(result)
                total_written += len(result)
                pbar.update(len(result))
                if total_written >= target_bytes:
                    break

        pbar.close()
        pool.close()
        pool.join()

        elapsed = time.time() - start_time
        print(f"\n✅ File generation complete: {total_written / (1024 * 1024):.2f} MB")
        print(f"⏱️ Elapsed time: {elapsed:.2f} seconds")

def main():
    try:
        mb_size = float(input("Required Output File Size (in MB): "))
    except ValueError:
        print("❌ Invalid input. Please enter a numeric value.")
        return

    target_bytes = int(mb_size * 1024 * 1024)
    num_qubits = 8
    filename = f"QRNG_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"

    write_parallel_random_data(num_qubits, target_bytes, filename)

if __name__ == "__main__":
    main()
