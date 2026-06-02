import os
import time
from datetime import datetime
import threading
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import tkinter as tk
from tkinter import ttk, messagebox

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

def write_random_data_until_size(num_qubits, target_bytes, filename, progress_callback):
    with open(filename, 'a') as file:
        total_written = 0
        start_time = time.time()
        while total_written < target_bytes:
            binary_number = generate_random_binary(num_qubits)
            file.write(binary_number)
            total_written += len(binary_number)
            progress_callback(total_written, target_bytes)
        elapsed = time.time() - start_time
        return total_written, elapsed

def start_generation(size_entry, qubits_entry, progressbar, label):
    try:
        mb_size = float(size_entry.get())
        num_qubits = int(qubits_entry.get())
        if num_qubits <= 0:
            raise ValueError
        target_bytes = int(mb_size * 1024 * 1024)
        filename = f"QRNG_3_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.txt"
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")
        return

    def progress_callback(current, total):
        progressbar["value"] = (current / total) * 100
        label.config(text=f"{current // 1024} KB written...")

    def thread_func():
        total_written, elapsed = write_random_data_until_size(num_qubits, target_bytes, filename, progress_callback)
        messagebox.showinfo("Completed", f"✅ File saved: {filename}\nSize: {total_written // 1024} KB\nTime: {elapsed:.2f} sec")

    threading.Thread(target=thread_func).start()

def main():
    root = tk.Tk()
    root.title("Quantum Random Number Generator")
    root.geometry("400x250")
    root.resizable(False, False)

    tk.Label(root, text="Output File Size (in MB):", font=("Arial", 12)).pack(pady=5)
    size_entry = tk.Entry(root, font=("Arial", 12))
    size_entry.pack()

    tk.Label(root, text="Number of Qubits:", font=("Arial", 12)).pack(pady=5)
    qubits_entry = tk.Entry(root, font=("Arial", 12))
    qubits_entry.insert(0, "2")  # Default value
    qubits_entry.pack()

    progress_label = tk.Label(root, text="Progress: 0 KB", font=("Arial", 10))
    progress_label.pack(pady=5)

    progressbar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progressbar.pack(pady=5)

    generate_button = tk.Button(root, text="Generate QRNG File", font=("Arial", 12), bg="#4CAF50", fg="white",
                                 command=lambda: start_generation(size_entry, qubits_entry, progressbar, progress_label))
    generate_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
