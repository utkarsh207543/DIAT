import hashlib
from qiskit import QuantumCircuit
from qiskit.primitives import Sampler
from qiskit_ibm_runtime import QiskitRuntimeService

# ==============================
# PARAMETERS
# ==============================
INPUT_FILE = "Utkarsh_QRNG_10.txt"
OUTPUT_FILE = "output_qiskit_mixed.txt"

TARGET_BITS = 2_000_000
QISKIT_BITS = 256_000     # auxiliary quantum entropy (safe, realistic)

# ==============================
# PARSE TIME-TAGGED DATA
# ==============================
def parse_qrng_file(filename):
    events = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%'):
                continue
            parts = line.split()
            try:
                if parts[0].isdigit():
                    events.append((int(parts[0]), '0'))
                if len(parts) > 1 and parts[1].isdigit():
                    events.append((int(parts[1]), '1'))
            except ValueError:
                continue

    events.sort(key=lambda x: x[0])
    return ''.join(bit for _, bit in events)

# ==============================
# VON NEUMANN EXTRACTOR
# ==============================
def von_neumann(bits):
    out = []
    for i in range(0, len(bits) - 1, 2):
        a, b = bits[i], bits[i + 1]
        if a != b:
            out.append(b)
    return ''.join(out)

# ==============================
# SHA-256 CONDITIONING (NOT ENTROPY INCREASE)
# ==============================
def sha256_condition(bits):
    data_bytes = int(bits, 2).to_bytes((len(bits) + 7) // 8, 'big')
    digest = hashlib.sha256(data_bytes).digest()
    return ''.join(f"{b:08b}" for b in digest)

# ==============================
# QISKIT: REAL QUANTUM ENTROPY
# ==============================
def get_quantum_bits(num_bits):
    """
    Fetch true quantum randomness from IBM Quantum hardware.
    """
    service = QiskitRuntimeService()
    backend = service.least_busy(simulator=False)

    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure_all()

    sampler = Sampler(backend=backend)

    bits = ""
    shots = 1024
    runs = (num_bits + shots - 1) // shots

    print(f"🔹 Using quantum backend: {backend.name}")

    for _ in range(runs):
        job = sampler.run(qc, shots=shots)
        result = job.result()
        counts = result.quasi_dists[0]

        for bit, prob in counts.items():
            bits += bit * int(prob * shots)

    return bits[:num_bits]

# ==============================
# XOR MIXING (ENTROPY MIXING)
# ==============================
def xor_mix(a, b):
    assert len(b) >= len(a)
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))

# ==============================
# EXPANSION (COUNTER + HASH)
# ==============================
def expand(bits, target_bits):
    out = ""
    counter = 0

    while len(out) < target_bits:
        data = bits + format(counter, '032b')
        data_bytes = int(data, 2).to_bytes((len(data) + 7) // 8, 'big')
        digest = hashlib.sha256(data_bytes).digest()
        out += ''.join(f"{b:08b}" for b in digest)
        counter += 1

    return out[:target_bits]

# ==============================
# MAIN PIPELINE
# ==============================
def qrng_pipeline():
    print("🔹 Parsing experimental QRNG data...")
    raw_bits = parse_qrng_file(INPUT_FILE)
    print(f"Raw bits: {len(raw_bits):,}")

    print("🔹 Von Neumann debiasing...")
    vn_bits = von_neumann(raw_bits)
    print(f"After VN: {len(vn_bits):,}")

    if len(vn_bits) < 20_000:
        raise RuntimeError("❌ Insufficient entropy after VN")

    print("🔹 Conditioning experimental entropy...")
    conditioned = sha256_condition(vn_bits)

    print("🔹 Fetching auxiliary quantum entropy (Qiskit)...")
    quantum_bits = get_quantum_bits(QISKIT_BITS)

    print("🔹 Mixing independent entropy sources...")
    mixed_seed = xor_mix(conditioned, quantum_bits)

    print("🔹 Expanding to target length...")
    final_bits = expand(mixed_seed, TARGET_BITS)

    with open(OUTPUT_FILE, "w") as f:
        f.write(final_bits)

    print(f"\n✅ SUCCESS: {TARGET_BITS:,} bits written to '{OUTPUT_FILE}'")

# ==============================
if __name__ == "__main__":
    qrng_pipeline()
