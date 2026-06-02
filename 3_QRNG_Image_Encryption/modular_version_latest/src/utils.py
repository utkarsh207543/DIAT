import numpy as np
import cv2
import os
from config import QRNG_PATH, OUT_DIR


def load_qrng_bytes():
    """Reads the QRNG text file and converts bits to bytes."""
    if not os.path.exists(QRNG_PATH):
        raise FileNotFoundError(f"QRNG file missing at: {QRNG_PATH}")

    with open(QRNG_PATH, "r") as f:
        bitstr = f.readline().strip()

    if not bitstr:
        raise ValueError("QRNG file is empty.")

    bits = np.array(list(bitstr), dtype=np.uint8)
    # Pack bits into bytes
    qrng_bytes = np.array([
        int("".join(bits[i * 8:(i + 1) * 8].astype(str)), 2)
        for i in range(len(bits) // 8)
    ], dtype=np.uint8)

    return qrng_bytes


def fisher_yates_shuffle(indices, qrng_bytes):
    """Deterministic Fisher-Yates shuffle using QRNG bytes."""
    idx = indices.copy()
    # Expand QRNG to match needed size
    q = np.tile(qrng_bytes, int(np.ceil(len(idx) / len(qrng_bytes)))).astype(np.uint32)

    for i in range(len(idx) - 1, 0, -1):
        j = int(q[i]) % (i + 1)
        idx[i], idx[j] = idx[j], idx[i]

    return idx


def save_stage(arr, filename):
    """Saves an intermediate image to the results folder."""
    path = os.path.join(OUT_DIR, filename)
    cv2.imwrite(path, arr)