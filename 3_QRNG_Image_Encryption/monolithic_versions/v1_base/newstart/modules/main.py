import os
import numpy as np
from PIL import Image
from quantum_cipher import QuantumCipher  # Imports your class from File 1

# ==========================================
# CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Input files (must exist in the base folder)
IMG_PATH = os.path.join(BASE_DIR, "cameraman.png")
QRNG_PATH = os.path.join(BASE_DIR, "QRNG.txt")

# Output paths (will be saved in results folder)
ENC_OUTPUT = os.path.join(RESULTS_DIR, "encrypted_output.png")
DEC_OUTPUT = os.path.join(RESULTS_DIR, "decrypted_output.png")


def main():
    # 1. Setup Environment
    print("--- Initializing ---")

    # Create results folder if it doesn't exist
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        print(f"Created folder: {RESULTS_DIR}")
    else:
        print(f"Saving to existing folder: {RESULTS_DIR}")

    cipher = QuantumCipher(QRNG_PATH)

    # 2. Load Original Image
    if not os.path.exists(IMG_PATH):
        print(f"ERROR: Image not found at {IMG_PATH}")
        return

    original_img = Image.open(IMG_PATH).convert("L")
    original_arr = np.array(original_img)
    print(f"Loaded image: {original_arr.shape}")

    # 3. Encrypt
    print("--- Encrypting ---")
    encrypted_arr = cipher.encrypt(original_arr)

    # Save Encrypted Image to Results Folder
    Image.fromarray(encrypted_arr).save(ENC_OUTPUT)
    print(f"Saved: {ENC_OUTPUT}")

    # 4. Decrypt
    print("--- Decrypting ---")
    decrypted_arr = cipher.decrypt(encrypted_arr)

    # Save Decrypted Image to Results Folder
    Image.fromarray(decrypted_arr).save(DEC_OUTPUT)
    print(f"Saved: {DEC_OUTPUT}")

    # 5. Validation
    if np.array_equal(original_arr, decrypted_arr):
        print("\n[SUCCESS] Decryption is perfect.")
    else:
        print("\n[FAIL] Decryption mismatch.")


if __name__ == "__main__":
    main()