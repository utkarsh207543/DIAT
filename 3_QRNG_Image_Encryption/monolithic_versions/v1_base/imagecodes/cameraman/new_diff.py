import numpy as np
import cv2, os
from PIL import Image

# =========================================================
# PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "cameraman.png")
QRNG_PATH = os.path.join(BASE, "QRNG.txt")

# =========================================================
# LOAD QRNG
# =========================================================
with open(QRNG_PATH, "r") as f:
    bitstr = f.readline().strip()
qrng_bytes = np.array([int(bitstr[i:i + 8], 2) for i in range(0, len(bitstr) - 7, 8)], dtype=np.uint8)


class QRNG_Fix:
    def __init__(self, img_np, qrng):
        self.work = img_np.copy().astype(np.uint8)
        self.m, self.n = self.work.shape
        # Expand QRNG to cover full image size
        self.Ks = np.tile(qrng, int(np.ceil((self.m * self.n) / len(qrng))))[:self.m * self.n]

    def fisher_yates_shuffle(self):
        """Confusion: Moves pixel positions."""
        flat = self.work.flatten()
        size = len(flat)
        # We must use a deterministic but random-looking index for the shuffle
        for i in range(size - 1, 0, -1):
            j = (int(self.Ks[i]) + i) % (i + 1)
            flat[i], flat[j] = flat[j], flat[i]
        self.work = flat.reshape((self.m, self.n))

    def diffuse(self):
        """
        Strong Diffusion: Bi-directional Modular Addition + XOR.
        This forces the avalanche effect.
        """
        flat = self.work.flatten().astype(np.int32)
        size = len(flat)

        # Forward Pass
        # We add the previous pixel value to the current one (Modular Addition)
        # This makes the current pixel's value dependent on ALL previous pixels
        for i in range(1, size):
            flat[i] = (flat[i] + flat[i - 1] + self.Ks[i]) % 256
            flat[i] = flat[i] ^ self.Ks[i]  # Extra XOR for randomness

        # Backward Pass
        # This propagates the change from the end of the image back to the start
        for i in range(size - 2, -1, -1):
            flat[i] = (flat[i] + flat[i + 1] + self.Ks[size - 1 - i]) % 256
            flat[i] = flat[i] ^ self.Ks[size - 1 - i]

        self.work = flat.reshape((self.m, self.n)).astype(np.uint8)

    def encrypt(self, rounds=2):
        for _ in range(rounds):
            self.fisher_yates_shuffle()
            self.diffuse()
        return self.work.copy()


# =========================================================
# THE TEST
# =========================================================
if __name__ == "__main__":
    img = Image.open(IMG_PATH).convert("L")
    arr1 = np.array(img)

    # Encrypt Image 1
    c1 = QRNG_Fix(arr1, qrng_bytes).encrypt()

    # Image 2 (Single Pixel Difference)
    arr2 = arr1.copy()
    arr2[0, 0] = np.uint8((int(arr2[0, 0]) + 1) % 256)
    c2 = QRNG_Fix(arr2, qrng_bytes).encrypt()

    # Calculate
    diff = (c1 != c2)
    npcr = np.sum(diff) / c1.size * 100
    uaci = np.mean(np.abs(c1.astype(float) - c2.astype(float))) / 255 * 100

    print("\n" + "=" * 30)
    print(f"NPCR: {npcr:.4f} %")
    print(f"UACI: {uaci:.4f} %")
    print("=" * 30)