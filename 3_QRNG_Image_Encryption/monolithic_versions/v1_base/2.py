import numpy as np
import cv2
import os
import json
import base64
import time
import math
import matplotlib.pyplot as plt
from PIL import Image
from skimage.util import random_noise
from scipy.stats import entropy

# =========================================================
# 1. SETUP & CONFIGURATION
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "mitu.png")
QRNG_PATH = os.path.join(BASE_DIR, "QRNG.txt")
KEY_PATH = os.path.join(BASE_DIR, "key.txt")

# --- AUTO-GENERATE DUMMY FILES IF MISSING (FOR DEMO) ---
if not os.path.exists(IMG_PATH):
    print(f"Warning: {IMG_PATH} not found. Generating a dummy random image for testing...")
    # Generate a random 256x256 color image
    dummy_img = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    Image.fromarray(dummy_img).save(IMG_PATH)

if not os.path.exists(QRNG_PATH):
    print(f"Warning: {QRNG_PATH} not found. Generating dummy QRNG data...")
    with open(QRNG_PATH, "w") as f:
        # Generate 100,000 random bits
        f.write("".join(str(np.random.randint(0, 2)) for _ in range(100000)))


# =========================================================
# 2. QRNG LOADER
# =========================================================
def load_qrng_bytes(path):
    with open(path, "r") as f:
        bitstr = f.readline().strip()

    qrng_bits = np.array(list(bitstr), dtype=np.uint8)
    if len(qrng_bits) < 8:
        # Fallback if file is too short
        qrng_bits = np.random.randint(0, 2, 8000, dtype=np.uint8)

    num_bytes = len(qrng_bits) // 8

    qrng_bytes = []
    for i in range(num_bytes):
        b = qrng_bits[i * 8:(i + 1) * 8]
        val = (b[0] << 7) | (b[1] << 6) | (b[2] << 5) | (b[3] << 4) | (b[4] << 3) | (b[5] << 2) | (b[6] << 1) | b[7]
        qrng_bytes.append(val)

    return np.array(qrng_bytes, dtype=np.uint8)


# Load QRNG data globally
qrng_data = load_qrng_bytes(QRNG_PATH)


# =========================================================
# 3. ENCRYPTION ENGINE (Rubik's Cube + QRNG)
# =========================================================
class RubikCubeCrypto:
    def __init__(self, image: Image.Image):
        self.image = image.convert("RGB")
        self.rgb = np.array(self.image, dtype=np.uint8)
        self.work = self.rgb.copy()
        self.m, self.n = self.rgb.shape[:2]
        self.Kr = []
        self.Kc = []
        self.iter_max = 1

    def create_key_from_qrng(self, qrng, iter_max=1):
        needed = self.m + self.n
        # Repeat qrng if not enough
        if len(qrng) < needed:
            qrng = np.tile(qrng, int(np.ceil(needed / len(qrng))))

        self.Kr = qrng[:self.m].tolist()
        self.Kc = qrng[self.m:self.m + self.n].tolist()
        self.iter_max = iter_max

        key = {"Kr": self.Kr, "Kc": self.Kc, "iter_max": iter_max}
        with open(KEY_PATH, "wb") as f:
            f.write(base64.b64encode(json.dumps(key).encode()))

    def load_key(self, custom_key_path=None):
        path = custom_key_path if custom_key_path else KEY_PATH
        with open(path, "rb") as f:
            key = json.loads(base64.b64decode(f.read()).decode())
        self.Kr = key["Kr"]
        self.Kc = key["Kc"]
        self.iter_max = key["iter_max"]

    def roll_rows(self, enc=True):
        d = 1 if enc else -1
        for i in range(self.m):
            s = self.Kr[i] % self.n
            self.work[i, :, :] = np.roll(self.work[i, :, :], d * s, axis=0)

    def roll_cols(self, enc=True):
        d = 1 if enc else -1
        for j in range(self.n):
            s = self.Kc[j] % self.m
            self.work[:, j, :] = np.roll(self.work[:, j, :], d * s, axis=0)

    def xor_pixels(self):
        # Broadcasting XOR mask
        kr = np.array(self.Kr, dtype=np.uint8).reshape(-1, 1, 1)  # (H, 1, 1)
        kc = np.array(self.Kc, dtype=np.uint8).reshape(1, -1, 1)  # (1, W, 1)
        mask = kr ^ kc
        self.work ^= mask

    def encrypt(self, qrng_source, iter_count=1):
        self.create_key_from_qrng(qrng_source, iter_count)
        for _ in range(self.iter_max):
            self.roll_rows(True)
            self.roll_cols(True)
            self.xor_pixels()
        return Image.fromarray(self.work)

    def decrypt(self, custom_key_path=None):
        self.load_key(custom_key_path)
        for _ in range(self.iter_max):
            self.xor_pixels()
            self.roll_cols(False)
            self.roll_rows(False)
        return Image.fromarray(self.work)


# =========================================================
# 4. METRICS & UTILITIES LIBRARY
# =========================================================
class Metrics:
    @staticmethod
    def mse(img1, img2):
        arr1 = np.array(img1, dtype=np.float64)
        arr2 = np.array(img2, dtype=np.float64)
        mse_val = np.mean((arr1 - arr2) ** 2)
        return mse_val

    @staticmethod
    def psnr(img1, img2):
        mse_val = Metrics.mse(img1, img2)
        if mse_val == 0: return 100
        return 10 * np.log10((255 ** 2) / mse_val)

    @staticmethod
    def entropy(img):
        gray = np.array(img.convert('L'))
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        prob = hist / hist.sum()
        # Filter zero probabilities to avoid log(0)
        prob = prob[prob > 0]
        return entropy(prob, base=2)

    @staticmethod
    def correlation(img, direction='horizontal'):
        arr = np.array(img.convert('L'), dtype=np.float64)
        if direction == 'horizontal':
            x = arr[:, :-1].flatten()
            y = arr[:, 1:].flatten()
        elif direction == 'vertical':
            x = arr[:-1, :].flatten()
            y = arr[1:, :].flatten()
        elif direction == 'diagonal':
            x = arr[:-1, :-1].flatten()
            y = arr[1:, 1:].flatten()
        else:
            return 0, [], []

        return np.corrcoef(x, y)[0, 1], x, y

    @staticmethod
    def npcr_uaci(img1, img2):
        arr1 = np.array(img1.convert('L'), dtype=int)
        arr2 = np.array(img2.convert('L'), dtype=int)

        diff = arr1 != arr2
        npcr = (np.sum(diff) / arr1.size) * 100
        uaci = (np.sum(np.abs(arr1 - arr2)) / (255 * arr1.size)) * 100
        return npcr, uaci


# =========================================================
# 5. MAIN ANALYSIS EXECUTION
# =========================================================
def run_analysis():
    print(">>> STARTING SECURITY ANALYSIS (As per Optik 327 (2025) 172304) <<<")

    # --- Load Images ---
    if not os.path.exists(IMG_PATH):
        print(f"Error: {IMG_PATH} not found.")
        return

    original_img = Image.open(IMG_PATH)
    orig_np = np.array(original_img)

    # --- 🔹 B & C: VISUALS AND PERFORMANCE ---
    print("\n[B & C] Performance & Visuals...")
    crypto = RubikCubeCrypto(original_img)

    start_time = time.time()
    enc_img = crypto.encrypt(qrng_data, iter_count=2)
    enc_time = time.time() - start_time

    start_time = time.time()
    dec_img = crypto.decrypt()
    dec_time = time.time() - start_time

    print(f" Encryption Time: {enc_time:.4f} s")
    print(f" Decryption Time: {dec_time:.4f} s")
    print(f" Decryption Perfect? {np.array_equal(orig_np, np.array(dec_img))}")

    # --- 🔹 D: STATISTICAL ANALYSIS ---
    print("\n[D] Statistical Analysis...")

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.hist(np.array(original_img.convert('L')).ravel(), bins=256, range=(0, 256), color='blue', alpha=0.7)
    plt.title("Original Histogram")
    plt.subplot(1, 2, 2)
    plt.hist(np.array(enc_img.convert('L')).ravel(), bins=256, range=(0, 256), color='red', alpha=0.7)
    plt.title("Encrypted Histogram")
    plt.savefig("histograms.png")
    print(" Saved 'histograms.png'")

    ent_orig = Metrics.entropy(original_img)
    ent_enc = Metrics.entropy(enc_img)
    print(f" Entropy (Original): {ent_orig:.5f}")
    [cite_start]
    print(f" Entropy (Encrypted): {ent_enc:.5f} (Ideal ~8.0)")[cite: 580]

    # --- 🔹 E: PIXEL CORRELATION ANALYSIS ---
    print("\n[E] Correlation Analysis...")
    directions = ['horizontal', 'vertical', 'diagonal']
    print(f"{'Direction':<12} | {'Original':<10} | {'Encrypted':<10}")
    print("-" * 38)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    for i, d in enumerate(directions):
        corr_o, xo, yo = Metrics.correlation(original_img, d)
        corr_e, xe, ye = Metrics.correlation(enc_img, d)

        print(f"{d.capitalize():<12} | {corr_o:.5f}    | {corr_e:.5f}")

        axes[0, i].scatter(xo[:2000], yo[:2000], s=0.5)
        axes[0, i].set_title(f"Orig {d.capitalize()}")
        axes[1, i].scatter(xe[:2000], ye[:2000], s=0.5, color='r')
        axes[1, i].set_title(f"Enc {d.capitalize()}")

    plt.tight_layout()
    plt.savefig("correlation_scatter.png")
    print(" Saved 'correlation_scatter.png'")

    # --- 🔹 F: DIFFERENTIAL ATTACK ANALYSIS (FIXED OVERFLOW) ---
    print("\n[F] Differential Attack (NPCR & UACI)...")

    arr_mod = np.array(original_img).copy()

    # FIX: Cast to int first to avoid OverflowError on uint8 + 1
    current_val = int(arr_mod[0, 0, 0])
    arr_mod[0, 0, 0] = (current_val + 1) % 256

    img_mod = Image.fromarray(arr_mod)

    c1 = RubikCubeCrypto(original_img).encrypt(qrng_data, iter_count=2)
    c2 = RubikCubeCrypto(img_mod).encrypt(qrng_data, iter_count=2)

    npcr, uaci = Metrics.npcr_uaci(c1, c2)
    [cite_start]
    print(f" NPCR: {npcr:.5f}% (Ideal > 99.6%)")[cite: 427]
    print(f" UACI: {uaci:.5f}% (Ideal ~ 33.4%)")

    # --- 🔹 G: NOISE ATTACK ANALYSIS ---
    print("\n[G] Noise Attack Resilience...")
    enc_np = np.array(enc_img)

    # 1. Salt & Pepper
    noise_sp = random_noise(enc_np, mode='s&p', amount=0.05)
    noise_sp = (255 * noise_sp).astype(np.uint8)
    dec_sp = RubikCubeCrypto(Image.fromarray(noise_sp)).decrypt()
    psnr_sp = Metrics.psnr(original_img, dec_sp)
    print(f" S&P Noise (0.05) -> Decrypted PSNR: {psnr_sp:.2f} dB")

    # 2. Gaussian
    noise_gauss = random_noise(enc_np, mode='gaussian', var=0.01)
    noise_gauss = (255 * noise_gauss).astype(np.uint8)
    dec_gauss = RubikCubeCrypto(Image.fromarray(noise_gauss)).decrypt()
    psnr_gauss = Metrics.psnr(original_img, dec_gauss)
    print(f" Gaussian Noise (0.01) -> Decrypted PSNR: {psnr_gauss:.2f} dB")

    Image.fromarray(noise_sp).save("noise_sp_enc.png")
    dec_sp.save("noise_sp_dec.png")

    # --- 🔹 H: KEY SENSITIVITY ANALYSIS ---
    print("\n[H] Key Sensitivity Analysis...")
    with open(KEY_PATH, "rb") as f:
        valid_key_data = json.loads(base64.b64decode(f.read()).decode())

    bad_key_data = valid_key_data.copy()
    # Ensure int arithmetic for the key modification
    bad_key_data["Kr"][0] = (int(bad_key_data["Kr"][0]) + 1) % 256

    with open("bad_key.txt", "wb") as f:
        f.write(base64.b64encode(json.dumps(bad_key_data).encode()))

    dec_bad = RubikCubeCrypto(enc_img).decrypt(custom_key_path="bad_key.txt")

    npcr_key, _ = Metrics.npcr_uaci(original_img, dec_bad)
    print(f" Decryption with perturbed key (1 bit change).")
    print(f" Difference from Original (NPCR): {npcr_key:.5f}% (Should be ~99.6% i.e., total fail)")
    dec_bad.save("key_sensitivity_fail.png")

    # --- 🔹 I: COMPARATIVE ANALYSIS ---
    print("\n[I] Comparative Analysis (vs Paper Table 6)...")
    print("-" * 65)
    print(f"{'Metric':<20} | {'Paper (Proposed)':<18} | {'Your Algorithm'}")
    print("-" * 65)
    [cite_start]
    print(f"{'Entropy':<20} | {'7.99981':<18} | {ent_enc:.5f}")[cite: 597]
    [cite_start]
    print(f"{'Corr (Hor)':<20} | {'0.0106':<18} | {corr_e:.4f}")[cite: 424]
    [cite_start]
    print(f"{'NPCR':<20} | {'99.63531':<18} | {npcr:.5f}")[cite: 597]
    [cite_start]
    print(f"{'PSNR (Decrypted)':<20} | {'27.91':<18} | {Metrics.psnr(original_img, dec_img):.2f}")[cite: 267]
    print("-" * 65)

    plt.figure(figsize=(10, 8))
    plt.subplot(2, 2, 1);
    plt.imshow(original_img);
    plt.title("Original")
    plt.subplot(2, 2, 2);
    plt.imshow(enc_img);
    plt.title("Encrypted")
    plt.subplot(2, 2, 3);
    plt.imshow(dec_sp);
    plt.title("Decrypted (S&P Noise)")
    plt.subplot(2, 2, 4);
    plt.imshow(dec_bad);
    plt.title("Key Sens. Fail")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run_analysis()