import numpy as np
import os
from PIL import Image

# =========================================================
# SETTINGS & PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "cameraman.png")  # Ensure this image exists
QRNG_PATH = os.path.join(BASE, "QRNG.txt")  # Ensure this file exists


# =========================================================
# CIPHER CLASS
# =========================================================
class QuantumImageCipher:
    def __init__(self, img_path, qrng_path):
        # 1. Load Image
        self.original_img = Image.open(img_path).convert("L")
        self.shape = np.array(self.original_img).shape
        self.height, self.width = self.shape
        self.total_pixels = self.height * self.width

        # 2. Load QRNG and create a Seed
        # We sum the bytes to create a seed for reproducibility
        with open(qrng_path, "r") as f:
            bitstr = f.readline().strip()

        # Parse bitstring to bytes
        qrng_bytes = [int(bitstr[i:i + 8], 2) for i in range(0, len(bitstr) - 7, 8)]

        # Create a seed from the QRNG file content
        # (In production, use a hash function like SHA256)
        self.seed = sum(qrng_bytes)

    def _generate_keys(self):
        """
        Generates deterministic random sequences based on the QRNG seed.
        We need:
        1. A permutation sequence for shuffling (indices)
        2. A key stream for diffusion (pixel values)
        """
        np.random.seed(self.seed)

        # 1. Generate Shuffle Indices (Fisher-Yates requirement)
        # For every pixel i, we need a random integer j in [0, i]
        # We generate this upfront to ensure Decryption can regenerate the EXACT same sequence
        self.shuffle_indices = np.array([np.random.randint(0, i + 1) for i in range(self.total_pixels)],
                                        dtype=np.uint32)

        # 2. Generate Diffusion Key Stream (0-255)
        self.key_stream = np.random.randint(0, 256, self.total_pixels, dtype=np.uint8)

    def _permutation(self, flat_img, mode='encrypt'):
        """
        Mathematically correct Fisher-Yates Shuffle.
        """
        arr = flat_img.copy()

        if mode == 'encrypt':
            # Iterate backwards: size-1 -> 1
            for i in range(self.total_pixels - 1, 0, -1):
                j = self.shuffle_indices[i]  # Deterministic random index
                arr[i], arr[j] = arr[j], arr[i]

        elif mode == 'decrypt':
            # Iterate forwards: 1 -> size-1
            # We must undo the swaps in the EXACT reverse order
            for i in range(1, self.total_pixels):
                j = self.shuffle_indices[i]
                arr[i], arr[j] = arr[j], arr[i]

        return arr

    def _diffusion(self, flat_img, mode='encrypt'):
        """
        Bidirectional Modular Addition + XOR.
        """
        arr = flat_img.astype(np.int32)
        keys = self.key_stream.astype(np.int32)

        if mode == 'encrypt':
            # --- Forward Pass ---
            # C[i] = (P[i] + C[i-1] + K[i]) % 256
            # XOR is applied after addition to mix bits
            prev = 0
            for i in range(self.total_pixels):
                val = (arr[i] + prev + keys[i]) % 256
                arr[i] = val ^ keys[i]  # XOR
                prev = arr[i]  # Update previous for next iteration

            # --- Backward Pass ---
            prev = 0
            for i in range(self.total_pixels - 1, -1, -1):
                val = (arr[i] + prev + keys[self.total_pixels - 1 - i]) % 256
                arr[i] = val ^ keys[self.total_pixels - 1 - i]
                prev = arr[i]

        elif mode == 'decrypt':
            # --- Inverse Backward Pass ---
            prev = 0
            for i in range(self.total_pixels - 1, -1, -1):
                # First undo XOR
                tmp = arr[i] ^ keys[self.total_pixels - 1 - i]
                # Then undo Addition (Subtract)
                val = (tmp - prev - keys[self.total_pixels - 1 - i]) % 256
                prev = arr[i]  # IMPORTANT: Use the ENCRYPTED value as 'prev' for next step
                arr[i] = val

            # --- Inverse Forward Pass ---
            prev = 0
            for i in range(self.total_pixels):
                tmp = arr[i] ^ keys[i]
                val = (tmp - prev - keys[i]) % 256
                prev = arr[i]  # Use ENCRYPTED value
                arr[i] = val

        return arr.astype(np.uint8)

    def process(self):
        # Generate the shared keys
        self._generate_keys()

        # --- ENCRYPTION ---
        print("Encrypting...")
        flat = np.array(self.original_img).flatten()

        # 1. Permutation (Shuffle)
        shuffled = self._permutation(flat, mode='encrypt')
        # 2. Diffusion (Mix values)
        encrypted_flat = self._diffusion(shuffled, mode='encrypt')

        encrypted_img = encrypted_flat.reshape(self.shape)

        # --- DECRYPTION ---
        print("Decrypting...")
        # 1. Inverse Diffusion
        un_diffused = self._diffusion(encrypted_flat, mode='decrypt')
        # 2. Inverse Permutation
        decrypted_flat = self._permutation(un_diffused, mode='decrypt')

        decrypted_img = decrypted_flat.reshape(self.shape)

        return encrypted_img, decrypted_img


# =========================================================
# MAIN EXECUTION
# =========================================================
if __name__ == "__main__":
    # Initialize Cipher
    cipher = QuantumImageCipher(IMG_PATH, QRNG_PATH)

    # Run Encrypt/Decrypt Cycle
    enc, dec = cipher.process()

    # Save Results
    Image.fromarray(enc).save("encrypted.png")
    Image.fromarray(dec).save("decrypted.png")

    print("\nDone!")
    print(f"Original Image Size: {cipher.shape}")

    # Verify Correctness
    original_arr = np.array(cipher.original_img)
    if np.array_equal(original_arr, dec):
        print("SUCCESS: Decrypted image matches Original perfectly.")
    else:
        print("FAILURE: Decryption did not recover original image.")