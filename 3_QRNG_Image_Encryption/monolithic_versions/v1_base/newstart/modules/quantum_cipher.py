import numpy as np
import os


class QuantumCipher:
    def __init__(self, qrng_path):
        self.qrng_path = qrng_path
        self.seed = self._load_qrng_seed()

    def _load_qrng_seed(self):
        """Reads QRNG file and creates a seed."""
        if not os.path.exists(self.qrng_path):
            raise FileNotFoundError(f"QRNG file not found at: {self.qrng_path}")

        with open(self.qrng_path, "r") as f:
            bitstr = f.readline().strip()

        if not bitstr:
            raise ValueError("QRNG file is empty.")

        # Convert bitstring to sum of bytes for the seed
        qrng_bytes = [int(bitstr[i:i + 8], 2) for i in range(0, len(bitstr) - 7, 8)]
        return sum(qrng_bytes)

    def _generate_keys(self, total_pixels):
        """Generates deterministic keys based on the QRNG seed."""
        np.random.seed(self.seed)

        # 1. Shuffle Indices (Fisher-Yates)
        indices = np.array([np.random.randint(0, i + 1) for i in range(total_pixels)], dtype=np.uint32)

        # 2. Diffusion Key Stream
        key_stream = np.random.randint(0, 256, total_pixels, dtype=np.uint8)

        return indices, key_stream

    def _fisher_yates(self, flat_img, indices, mode):
        """Permutation Logic"""
        arr = flat_img.copy()
        size = len(arr)

        if mode == 'encrypt':
            for i in range(size - 1, 0, -1):
                j = indices[i]
                arr[i], arr[j] = arr[j], arr[i]
        elif mode == 'decrypt':
            for i in range(1, size):
                j = indices[i]
                arr[i], arr[j] = arr[j], arr[i]
        return arr

    def _diffusion(self, flat_img, keys, mode):
        """Diffusion Logic"""
        arr = flat_img.astype(np.int32)
        keys = keys.astype(np.int32)
        size = len(arr)

        if mode == 'encrypt':
            prev = 0
            # Forward
            for i in range(size):
                val = (arr[i] + prev + keys[i]) % 256
                arr[i] = val ^ keys[i]
                prev = arr[i]
            # Backward
            prev = 0
            for i in range(size - 1, -1, -1):
                val = (arr[i] + prev + keys[size - 1 - i]) % 256
                arr[i] = val ^ keys[size - 1 - i]
                prev = arr[i]

        elif mode == 'decrypt':
            # Inverse Backward
            prev = 0
            for i in range(size - 1, -1, -1):
                tmp = arr[i] ^ keys[size - 1 - i]
                val = (tmp - prev - keys[size - 1 - i]) % 256
                prev = arr[i]
                arr[i] = val
            # Inverse Forward
            prev = 0
            for i in range(size):
                tmp = arr[i] ^ keys[i]
                val = (tmp - prev - keys[i]) % 256
                prev = arr[i]
                arr[i] = val

        return arr.astype(np.uint8)

    def encrypt(self, img_arr):
        """Public method to encrypt an image array."""
        flat = img_arr.flatten()
        indices, keys = self._generate_keys(len(flat))

        # 1. Shuffle -> 2. Diffuse
        shuffled = self._fisher_yates(flat, indices, 'encrypt')
        encrypted = self._diffusion(shuffled, keys, 'encrypt')

        return encrypted.reshape(img_arr.shape)

    def decrypt(self, encrypted_arr):
        """Public method to decrypt an image array."""
        flat = encrypted_arr.flatten()
        indices, keys = self._generate_keys(len(flat))

        # 1. Inverse Diffuse -> 2. Inverse Shuffle
        undiffused = self._diffusion(flat, keys, 'decrypt')
        decrypted = self._fisher_yates(undiffused, indices, 'decrypt')

        return decrypted.reshape(encrypted_arr.shape)