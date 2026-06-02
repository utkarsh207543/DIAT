import numpy as np
import cv2, os
from PIL import Image

# =========================================================
# PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "mitu.png")
QRNG_PATH = os.path.join(BASE, "QRNG.txt")
OUT_DIR = os.path.join(BASE, "results_final")
os.makedirs(OUT_DIR, exist_ok=True)

# Load QRNG
with open(QRNG_PATH, "r") as f:
    bitstr = f.readline().strip()
qrng_bytes = np.array([int(bitstr[i:i + 8], 2) for i in range(0, len(bitstr) - 7, 8)], dtype=np.uint8)


# =========================================================
# CRYPTO ENGINE
# =========================================================
class QRNG_Rubik:
    def __init__(self, img_np, qrng):
        self.work = img_np.copy().astype(np.uint8)
        self.m, self.n = self.work.shape
        # Tile keys to match image dimensions
        q = np.tile(qrng, int(np.ceil((self.m + self.n) / len(qrng))))
        self.Kr = q[:self.m]
        self.Kc = q[self.m:self.m + self.n]

    def roll(self):
        # Row Roll
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i], int(self.Kr[i]))
        # Column Roll
        for j in range(self.n):
            self.work[:, j] = np.roll(self.work[:, j], int(self.Kc[j]))

    def diffuse(self):
        """Global Bi-directional Diffusion"""
        flat = self.work.flatten().astype(np.int32)
        size = len(flat)

        # 1. Forward Pass (Spreads change to the end)
        for i in range(1, size):
            # XOR current pixel with previous, plus QRNG key component
            flat[i] = (flat[i] ^ flat[i - 1] ^ self.Kr[i % self.m]) & 0xFF

        # 2. Backward Pass (Spreads change back to the start)
        for i in range(size - 2, -1, -1):
            flat[i] = (flat[i] ^ flat[i + 1] ^ self.Kc[i % self.n]) & 0xFF

        self.work = flat.reshape((self.m, self.n)).astype(np.uint8)

    def encrypt(self, rounds=2):
        for _ in range(rounds):
            self.roll()
            self.diffuse()
        return self.work.copy()


# =========================================================
# DIFFERENTIAL TEST
# =========================================================
if __name__ == "__main__":
    # Load Image
    img = Image.open(IMG_PATH).convert("L")
    arr1 = np.array(img)

    # Image 1 Encryption
    cipher1 = QRNG_Rubik(arr1, qrng_bytes).encrypt()

    # Image 2: Modify exactly one pixel [0,0]
    arr2 = arr1.copy()
    arr2[0, 0] = np.uint8((int(arr2[0, 0]) + 1) % 256)
    cipher2 = QRNG_Rubik(arr2, qrng_bytes).encrypt()

    # Calculate NPCR & UACI
    diff = (cipher1 != cipher2)
    NPCR = np.sum(diff) / cipher1.size * 100
    UACI = np.mean(np.abs(cipher1.astype(float) - cipher2.astype(float))) / 255 * 100

    print(f"\n[RESULTS]")
    print(f"NPCR: {NPCR:.4f} %  (Should be > 99.6%)")
    print(f"UACI: {UACI:.4f} %  (Should be ~ 33.4%)")

    cv2.imwrite(os.path.join(OUT_DIR, "c1.png"), cipher1)
    cv2.imwrite(os.path.join(OUT_DIR, "c2.png"), cipher2)