import numpy as np
import cv2, os, json, base64, time
from PIL import Image
import matplotlib.pyplot as plt
from skimage.util import random_noise
from skimage.metrics import structural_similarity as ssim
import math

# =========================================================
# PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "cameraman.png")
QRNG_PATH = os.path.join(BASE, "QRNG.txt")
KEY_PATH = os.path.join(BASE, "key.txt")
OUT_DIR = os.path.join(BASE, "results_final")
os.makedirs(OUT_DIR, exist_ok=True)


# =========================================================
# METRICS & UTILITIES
# =========================================================

def NPCR(img1, img2):
    return np.sum(img1 != img2) / img1.size * 100


def UACI(img1, img2):
    return np.mean(np.abs(img1.astype(np.float32) - img2.astype(np.float32))) / 255 * 100


def mse(a, b): return np.mean((a.astype(float) - b.astype(float)) ** 2)


def psnr(a, b): return np.inf if mse(a, b) == 0 else 10 * np.log10(255 ** 2 / mse(a, b))


def ssim_index(a, b):
    return ssim(a, b, data_range=255)


def entropy(img):
    hist, _ = np.histogram(img.flatten(), 256, (0, 255))
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


def corr(a, b):
    return np.corrcoef(a.flatten(), b.flatten())[0, 1]


def corr_coefficients(img):
    H = corr(img[:, :-1], img[:, 1:])  # Horizontal
    V = corr(img[:-1, :], img[1:, :])  # Vertical
    D = corr(img[:-1, :-1], img[1:, 1:])  # Diagonal
    return H, V, D


def save_stage(arr, name):
    cv2.imwrite(os.path.join(OUT_DIR, name), arr)


def correlation_plot(img, direction, title, filename, samples=5000):
    if direction == "H":
        x = img[:, :-1].flatten()
        y = img[:, 1:].flatten()
    elif direction == "V":
        x = img[:-1, :].flatten()
        y = img[1:, :].flatten()
    elif direction == "D":
        x = img[:-1, :-1].flatten()
        y = img[1:, 1:].flatten()
    else:
        return

    idx = np.random.choice(len(x), size=min(samples, len(x)), replace=False)
    plt.figure(figsize=(4, 4))
    plt.scatter(x[idx], y[idx], s=1, c='black', alpha=0.5)
    plt.title(title)
    plt.xlabel("Pixel (x)")
    plt.ylabel("Neighbor (y)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


def save_histogram(img, title, filename):
    plt.figure(figsize=(5, 4))
    plt.hist(img.flatten(), bins=256, range=(0, 255), density=True, color='gray', alpha=0.7)
    plt.title(title)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


# =========================================================
# LOAD QRNG
# =========================================================
if not os.path.exists(QRNG_PATH):
    # Dummy QRNG for testing if file missing
    with open(QRNG_PATH, "w") as f:
        f.write("10011010" * 10000)

with open(QRNG_PATH, "r") as f:
    bitstr = f.readline().strip()

bits = np.array(list(bitstr), dtype=np.uint8)
qrng_bytes = np.array([
    int("".join(bits[i * 8:(i + 1) * 8].astype(str)), 2)
    for i in range(len(bits) // 8)
], dtype=np.uint8)


# =========================================================
# HIGH-PERFORMANCE CRYPTO CLASS
# =========================================================
class RubikCubeCrypto:

    def __init__(self, image_np, qrng_bytes):
        # Ensure we work on Grayscale for standard crypto metrics
        if len(image_np.shape) == 3:
            self.work = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        else:
            self.work = image_np.copy()

        self.m, self.n = self.work.shape
        self.qrng = qrng_bytes
        self.generate_keys()

    def generate_keys(self):
        # Create full key stream from QRNG
        total_pixels = self.m * self.n
        needed = total_pixels + self.m + self.n

        # Expand QRNG if too small
        q = np.tile(self.qrng, int(np.ceil(needed / len(self.qrng))))

        self.Kr = q[:self.m].astype(np.int32)
        self.Kc = q[self.m: self.m + self.n].astype(np.int32)
        # Stream Key for Diffusion
        self.Ks = q[self.m + self.n: self.m + self.n + total_pixels].astype(np.int32)

    def fisher_yates_shuffle(self, enc=True):
        """Reversible Fisher-Yates based on QRNG seed"""
        flat = self.work.flatten()
        size = len(flat)
        # Use a deterministic generator seeded by QRNG to make shuffle reversible
        seed = int(self.Ks[0])
        rng = np.random.RandomState(seed)
        p = rng.permutation(size)

        if enc:
            self.work = flat[p].reshape((self.m, self.n))
        else:
            inv = np.empty_like(p)
            inv[p] = np.arange(size)
            self.work = flat[inv].reshape((self.m, self.n))

    def roll(self, enc=True):
        d = 1 if enc else -1
        # Row Roll
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i], d * (self.Kr[i] % self.n))
        # Col Roll
        for j in range(self.n):
            self.work[:, j] = np.roll(self.work[:, j], d * (self.Kc[j] % self.m))

    def diffuse(self, enc=True):
        """Bi-directional Modular Diffusion (The NPCR Booster)"""
        flat = self.work.flatten().astype(np.int32)
        size = len(flat)

        if enc:
            # Forward: Add previous pixel + Key
            for i in range(1, size):
                flat[i] = (flat[i] + flat[i - 1] + self.Ks[i]) % 256
                flat[i] ^= self.Ks[i]  # XOR for non-linearity

            # Backward: Add next pixel + Key
            for i in range(size - 2, -1, -1):
                flat[i] = (flat[i] + flat[i + 1] + self.Ks[size - 1 - i]) % 256
                flat[i] ^= self.Ks[size - 1 - i]

        else:
            # Reverse Backward Pass
            for i in range(0, size - 1):
                flat[i] ^= self.Ks[size - 1 - i]
                flat[i] = (flat[i] - flat[i + 1] - self.Ks[size - 1 - i]) % 256

            # Reverse Forward Pass
            for i in range(size - 1, 0, -1):
                flat[i] ^= self.Ks[i]
                flat[i] = (flat[i] - flat[i - 1] - self.Ks[i]) % 256

        self.work = flat.reshape((self.m, self.n)).astype(np.uint8)

    def encrypt(self, rounds=2):
        for _ in range(rounds):
            self.fisher_yates_shuffle(enc=True)
            self.roll(enc=True)
            self.diffuse(enc=True)
        return self.work.copy()

    def decrypt(self, rounds=2):
        for _ in range(rounds):
            self.diffuse(enc=False)
            self.roll(enc=False)
            self.fisher_yates_shuffle(enc=False)
        return self.work.copy()


# =========================================================
# MAIN EXECUTION FLOW
# =========================================================

# 1. Load Original Image
if not os.path.exists(IMG_PATH):
    # Create dummy if missing
    dummy = np.random.randint(0, 256, (256, 256), dtype=np.uint8)
    cv2.imwrite(IMG_PATH, dummy)

orig_pil = Image.open(IMG_PATH).convert("L")
orig_np = np.array(orig_pil)
save_stage(orig_np, "01_original.png")

# 2. Encryption
t0 = time.time()
engine = RubikCubeCrypto(orig_np, qrng_bytes)
enc_np = engine.encrypt()
t_enc = time.time() - t0
save_stage(enc_np, "02_encrypted.png")

# 3. Decryption
t0 = time.time()
dec_engine = RubikCubeCrypto(enc_np, qrng_bytes)
dec_np = dec_engine.decrypt()
t_dec = time.time() - t0
save_stage(dec_np, "03_decrypted.png")

# 4. Differential Attack (NPCR/UACI)
# Create modified image (1 pixel change)
orig_diff = orig_np.copy()
orig_diff[0, 0] = np.uint8((int(orig_diff[0, 0]) + 1) % 256)

# Encrypt both with SAME engine logic/keys
enc_1 = RubikCubeCrypto(orig_np, qrng_bytes).encrypt()
enc_2 = RubikCubeCrypto(orig_diff, qrng_bytes).encrypt()

npcr_val = NPCR(enc_1, enc_2)
uaci_val = UACI(enc_1, enc_2)

# 5. Metrics Calculation & Plotting
H_orig = entropy(orig_np)
H_enc = entropy(enc_np)
H_dec = entropy(dec_np)

ssim_val = ssim_index(orig_np, dec_np)
mse_val = mse(orig_np, dec_np)
psnr_val = psnr(orig_np, dec_np)

# Correlation Coefficients
Ho, Vo, Do = corr_coefficients(orig_np)
He, Ve, De = corr_coefficients(enc_np)

# Generate Plots
save_histogram(orig_np, "Original Histogram", "hist_orig.png")
save_histogram(enc_np, "Encrypted Histogram", "hist_enc.png")

correlation_plot(orig_np, "H", "Original Horizontal", "corr_orig_h.png")
correlation_plot(enc_np, "H", "Encrypted Horizontal", "corr_enc_h.png")
correlation_plot(orig_np, "D", "Original Diagonal", "corr_orig_d.png")
correlation_plot(enc_np, "D", "Encrypted Diagonal", "corr_enc_d.png")

# 6. Save Report
with open(os.path.join(OUT_DIR, "final_metrics.txt"), "w") as f:
    f.write("=== QRNG ENCRYPTION REPORT ===\n\n")
    f.write(f"Encryption Time: {t_enc:.4f} s\n")
    f.write(f"Decryption Time: {t_dec:.4f} s\n\n")

    f.write("=== DIFFERENTIAL ATTACK (Target: >99.6% / ~33.4%) ===\n")
    f.write(f"NPCR: {npcr_val:.4f} %\n")
    f.write(f"UACI: {uaci_val:.4f} %\n\n")

    f.write("=== INFORMATION ENTROPY (Target: ~8.0) ===\n")
    f.write(f"Original:  {H_orig:.4f}\n")
    f.write(f"Encrypted: {H_enc:.4f}\n\n")

    f.write("=== QUALITY METRICS ===\n")
    f.write(f"MSE:  {mse_val:.4f}\n")
    f.write(f"PSNR: {psnr_val:.4f} dB\n")
    f.write(f"SSIM: {ssim_val:.4f} (1.0 = Perfect Reconstruction)\n\n")

    f.write("=== CORRELATION (Original / Encrypted) ===\n")
    f.write(f"Horizontal: {Ho:.4f} / {He:.4f}\n")
    f.write(f"Vertical:   {Vo:.4f} / {Ve:.4f}\n")
    f.write(f"Diagonal:   {Do:.4f} / {De:.4f}\n")

print(f"Done! Results saved in {OUT_DIR}")
print(f"NPCR: {npcr_val:.4f}% | UACI: {uaci_val:.4f}%")