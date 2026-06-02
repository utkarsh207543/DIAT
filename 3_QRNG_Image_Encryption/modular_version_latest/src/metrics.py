import numpy as np
import matplotlib.pyplot as plt
import os
import math
from skimage.util import random_noise
from skimage.metrics import structural_similarity as ssim
from PIL import Image

from config import OUT_DIR, METRICS_FILE
from crypto_engine import RubikCubeCrypto
from utils import save_stage


# --- METRIC FUNCTIONS ---

def NPCR(img1, img2):
    diff = img1 != img2
    return np.sum(diff) / diff.size * 100


def UACI(img1, img2):
    return np.mean(np.abs(img1.astype(np.int16) - img2.astype(np.int16))) / 255 * 100


def mse(a, b):
    return np.mean((a.astype(float) - b.astype(float)) ** 2)


def psnr(a, b):
    m = mse(a, b)
    return np.inf if m == 0 else 10 * np.log10(255 ** 2 / m)


def entropy(img):
    hist, _ = np.histogram(img.flatten(), 256, (0, 255))
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


def ssim_index(a, b):
    return ssim(a, b, data_range=255)


def brute_force_time_estimate_log(key_bits, trials_per_second=1e12):
    log10_seconds = key_bits * math.log10(2) - math.log10(trials_per_second)
    log10_years = log10_seconds - math.log10(60 * 60 * 24 * 365)
    return log10_seconds, log10_years


# --- ATTACK SIMULATIONS ---

def run_differential_attack(orig_np, qrng_bytes):
    # 1. Modify one pixel
    orig_diff = orig_np.copy().astype(np.int16)
    orig_diff[0, 0] = (orig_diff[0, 0] + 128) % 256
    orig_diff = orig_diff.astype(np.uint8)

    # 2. Encrypt Original
    c1 = RubikCubeCrypto(Image.fromarray(orig_np))
    enc1 = c1.encrypt(qrng_bytes, tag="diff_orig_")

    # 3. Encrypt Modified (Reuse same key structure/indices)
    c2 = RubikCubeCrypto(Image.fromarray(orig_diff))
    c2.bp_index = c1.bp_index  # Force same block shuffle
    c2.load_key()  # Force same rolling keys
    enc2 = c2.encrypt(qrng_bytes, use_existing_key=True, tag="diff_mod_")

    e1 = np.array(enc1.convert("L"))
    e2 = np.array(enc2.convert("L"))
    return NPCR(e1, e2), UACI(e1, e2)


def noise_attacks(enc_np, qrng_bytes):
    results = {}

    # Salt & Pepper
    noisy = random_noise(enc_np, mode='s&p', amount=0.05)
    sp_img = (255 * noisy).astype(np.uint8)
    save_stage(sp_img, "attack_01_salt_pepper.png")
    # Decrypt
    dec_sp = np.array(RubikCubeCrypto(Image.fromarray(sp_img)).decrypt(tag="sp_").convert("L"))
    results['sp'] = dec_sp

    # Gaussian
    noisy = random_noise(enc_np, mode='gaussian', var=0.001)
    gauss_img = (255 * noisy).astype(np.uint8)
    save_stage(gauss_img, "attack_02_gaussian.png")
    # Decrypt
    dec_gauss = np.array(RubikCubeCrypto(Image.fromarray(gauss_img)).decrypt(tag="gauss_").convert("L"))
    results['gauss'] = dec_gauss

    return results


# --- PLOTTING ---

def save_histogram(img, title, filename):
    plt.figure(figsize=(5, 4))
    plt.hist(img.flatten(), bins=256, range=(0, 255), density=True)
    plt.title(title)
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


def correlation_plot(img, direction, title, filename):
    if direction == "H":
        x, y = img[:, :-1].flatten(), img[:, 1:].flatten()
    elif direction == "V":
        x, y = img[:-1, :].flatten(), img[1:, :].flatten()
    elif direction == "D":
        x, y = img[:-1, :-1].flatten(), img[1:, 1:].flatten()

    idx = np.random.choice(len(x), size=min(5000, len(x)), replace=False)
    plt.figure(figsize=(4, 4))
    plt.scatter(x[idx], y[idx], s=1)
    plt.title(title)
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


def generate_report(orig_np, enc_np, dec_np, t_enc, t_dec, npcr, uaci):
    h_orig, h_enc = entropy(orig_np), entropy(enc_np)
    s_val = ssim_index(orig_np, dec_np)
    m_val = mse(orig_np, dec_np)
    p_val = psnr(orig_np, dec_np)

    report = [
        "=== QUANTUM CRYPTO ANALYSIS REPORT ===",
        f"Encryption Time: {t_enc:.4f}s",
        f"Decryption Time: {t_dec:.4f}s",
        "",
        "=== SECURITY METRICS (Cipher) ===",
        f"Entropy (Original):  {h_orig:.4f}",
        f"Entropy (Encrypted): {h_enc:.4f} (Target: ~8.0)",
        f"NPCR: {npcr:.4f}% (Target: >99.6%)",
        f"UACI: {uaci:.4f}% (Target: ~33.4%)",
        "",
        "=== QUALITY METRICS (Reconstruction) ===",
        f"MSE:  {m_val:.4f}",
        f"PSNR: {p_val:.4f} dB",
        f"SSIM: {s_val:.4f} (1.0 = Perfect match)",
    ]

    with open(METRICS_FILE, "w") as f:
        f.write("\n".join(report))
    print(f"Report saved to {METRICS_FILE}")