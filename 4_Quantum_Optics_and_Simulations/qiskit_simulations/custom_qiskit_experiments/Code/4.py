from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit import transpile
from datetime import datetime
import matplotlib.pyplot as plt

def get_single_bit(simulator, transpile_seed=None):
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    compiled = transpile(qc, simulator, seed_transpiler=transpile_seed)
    result = simulator.run(compiled, shots=1).result()
    bit = list(result.get_counts().keys())[0]
    return bit

def generate_entropy_bits(num_bits=8192, output_file="output.txt"):
    simulator = AerSimulator()
    raw_bits = []

    # Collect single qubit outcomes
    for i in range(num_bits):
        bit = get_single_bit(simulator, transpile_seed=i)
        raw_bits.append(bit)

    # Optional: XOR folding for debiasing
    def xor_fold(bits):
        folded = []
        for i in range(0, len(bits) - 1, 2):
            folded.append(str(int(bits[i]) ^ int(bits[i + 1])))
        return folded

    post_processed = xor_fold(raw_bits)

    # Save to file
    with open(output_file, "w") as f:
        f.write("".join(post_processed))

    print(f"{len(post_processed)} post-processed bits written to {output_file}")

# Visualize the 1-qubit circuit
#qc = QuantumCircuit(1, 1)
#qc.h(0)
#qc.measure(0, 0)
#qc.draw(output='mpl')
#plt.title("1-Qubit QRNG Circuit")
#plt.tight_layout()
#plt.show()

# Run QRNG
generate_entropy_bits()
