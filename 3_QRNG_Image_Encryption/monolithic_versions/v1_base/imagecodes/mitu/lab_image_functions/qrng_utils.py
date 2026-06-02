import numpy as np
from config import QRNG_PATH

# =========================================================
# LOAD QRNG BITS → BYTES
# =========================================================
def load_qrng_bytes():
    """Load QRNG from file and convert to bytes"""
    with open(QRNG_PATH, "r") as f:
        bitstr = f.readline().strip()
    
    bits = np.array(list(bitstr), dtype=np.uint8)
    qrng_bytes = np.array([
        int("".join(bits[i*8:(i+1)*8].astype(str)), 2)
        for i in range(len(bits)//8)
    ], dtype=np.uint8)
    
    return qrng_bytes

# =========================================================
# FISHER–YATES SHUFFLE (SAFE INTEGER VERSION)
# =========================================================
def fisher_yates_shuffle(indices, qrng):
    """
    Fisher-Yates shuffle using QRNG for randomization
    
    Args:
        indices: List of indices to shuffle
        qrng: QRNG bytes array
    
    Returns:
        Shuffled indices
    """
    idx = indices.copy()
    q = np.tile(qrng, int(np.ceil(len(idx)/len(qrng)))).astype(np.uint32)

    for i in range(len(idx)-1, 0, -1):
        j = int(q[i]) % (i+1)
        idx[i], idx[j] = idx[j], idx[i]

    return idx

# Load QRNG globally
qrng_bytes = load_qrng_bytes()
