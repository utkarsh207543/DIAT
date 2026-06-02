import time
import numpy as np
from PIL import Image

# Import custom modules
from config import IMG_PATH, QRNG_PATH
from utils import load_qrng_bytes, save_stage
from crypto_engine import RubikCubeCrypto
import metrics


def main():
    print("--- 1. LOADING RESOURCES ---")
    qrng_bytes = load_qrng_bytes()

    orig = Image.open(IMG_PATH)
    orig_np = np.array(orig.convert("L"))
    save_stage(orig_np, "00_original_input.png")

    # ---------------- ENCRYPTION ----------------
    print("--- 2. ENCRYPTING ---")
    cipher = RubikCubeCrypto(orig)

    t0 = time.time()
    enc_img = cipher.encrypt(qrng_bytes, tag="main_")
    t_enc = time.time() - t0

    enc_np = np.array(enc_img.convert("L"))
    print(f"Encryption Complete ({t_enc:.3f}s)")

    # ---------------- ATTACKS & ANALYSIS ----------------
    print("--- 3. PERFORMING SECURITY ANALYSIS ---")
    # Histograms
    metrics.save_histogram(orig_np, "Original Hist", "hist_orig.png")
    metrics.save_histogram(enc_np, "Encrypted Hist", "hist_enc.png")

    # Correlation
    metrics.correlation_plot(orig_np, "H", "Orig Corr (H)", "corr_orig_h.png")
    metrics.correlation_plot(enc_np, "H", "Enc Corr (H)", "corr_enc_h.png")

    # Differential Attack (NPCR/UACI)
    print("Running Differential Attack...")
    npcr, uaci = metrics.run_differential_attack(orig_np, qrng_bytes)

    # Noise Attacks
    print("Running Noise Attacks...")
    metrics.noise_attacks(enc_np, qrng_bytes)

    # ---------------- DECRYPTION ----------------
    print("--- 4. DECRYPTING ---")
    # Initialize new instance with Encrypted image
    decipher = RubikCubeCrypto(enc_img)

    t0 = time.time()
    dec_img = decipher.decrypt(tag="main_")
    t_dec = time.time() - t0

    dec_np = np.array(dec_img.convert("L"))
    print(f"Decryption Complete ({t_dec:.3f}s)")

    # ---------------- REPORT ----------------
    metrics.generate_report(orig_np, enc_np, dec_np, t_enc, t_dec, npcr, uaci)
    print("\nSUCCESS: All results saved in 'results' folder.")


if __name__ == "__main__":
    main()