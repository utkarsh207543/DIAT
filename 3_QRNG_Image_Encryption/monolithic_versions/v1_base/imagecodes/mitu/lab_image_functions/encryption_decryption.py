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
OUT_DIR = os.path.join(BASE, "results")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================================================
# METRICS
# =========================================================

def brute_force_time_estimate_log(key_bits, trials_per_second=1e12):
    """
    Logarithmic brute-force time estimation (overflow-safe).
    Returns log10(seconds) and log10(years).
    """
    log10_total_keys = key_bits * math.log10(2)
    log10_trials_per_sec = math.log10(trials_per_second)

    log10_seconds = log10_total_keys - log10_trials_per_sec
    log10_years = log10_seconds - math.log10(60*60*24*365)

    return log10_seconds, log10_years



def NPCR(img1, img2):
    assert img1.shape == img2.shape

    if img1.ndim == 3:  # RGB
        diff = np.any(img1 != img2, axis=2)
    else:               # Grayscale
        diff = img1 != img2

    return np.sum(diff) / diff.size * 100

def UACI(img1, img2):
    assert img1.shape == img2.shape
    return np.mean(np.abs(img1.astype(np.int16) - img2.astype(np.int16))) / 255 * 100



def qrng_noise_attack(img, qrng, strength=0.1):
    """
    QRNG-driven noise attack using hardware entropy
    strength: fraction of max intensity (0–1)
    """
    h, w = img.shape
    total = h * w

    q = np.tile(qrng, int(np.ceil(total / len(qrng))))
    q = q[:total].astype(np.int16)

    # Map QRNG to noise in [-A, +A]
    A = int(255 * strength)
    noise = (q % (2*A+1)) - A
    noise = noise.reshape(h, w)

    noisy = img.astype(np.int16) + noise
    noisy = np.clip(noisy, 0, 255)

    return noisy.astype(np.uint8)


def gaussian_attack(img, var=0.001):
    noisy = random_noise(img, mode='gaussian', var=var)
    return (255 * noisy).astype(np.uint8)


def salt_pepper_attack(img, amount=0.05):
    noisy = random_noise(img, mode='s&p', amount=amount)
    return (255 * noisy).astype(np.uint8)


def ssim_index(a, b):
    return ssim(a, b, data_range=255)

def blocking_attack(img, block_ratio=0.2):
    """
    Zero out a central block of the encrypted image.
    block_ratio: fraction of image size to block
    """
    attacked = img.copy()
    h, w = img.shape

    bh = int(h * block_ratio)
    bw = int(w * block_ratio)

    y0 = (h - bh) // 2
    x0 = (w - bw) // 2

    attacked[y0:y0+bh, x0:x0+bw] = 0
    return attacked

def corr(a,b):
    return np.corrcoef(a.flatten(),b.flatten())[0,1]

def corr_coefficients(img):
    H = corr(img[:, :-1], img[:, 1:])       # Horizontal
    V = corr(img[:-1, :], img[1:, :])       # Vertical
    D = corr(img[:-1, :-1], img[1:, 1:])    # Diagonal
    return H, V, D

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
        raise ValueError("Direction must be H, V, or D")

    idx = np.random.choice(len(x), size=min(samples, len(x)), replace=False)

    plt.figure(figsize=(4,4))
    plt.scatter(x[idx], y[idx], s=1)
    plt.title(title)
    plt.xlabel("Pixel value (i)")
    plt.ylabel("Pixel value (j)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()

def save_histogram(img, title, filename):
    plt.figure(figsize=(5,4))
    plt.hist(img.flatten(), bins=256, range=(0,255), density=True)
    plt.title(title)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Probability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()

def mse(a,b): return np.mean((a.astype(float)-b.astype(float))**2)
def psnr(a,b): return np.inf if mse(a,b)==0 else 10*np.log10(255**2/mse(a,b))

def entropy(img):
    hist,_ = np.histogram(img.flatten(),256,(0,255))
    p = hist/np.sum(hist)
    p = p[p>0]
    return -np.sum(p*np.log2(p))



def save_stage(arr, name):
    cv2.imwrite(os.path.join(OUT_DIR, name), arr)

# =========================================================
# LOAD QRNG BITS → BYTES
# =========================================================
with open(QRNG_PATH,"r") as f:
    bitstr = f.readline().strip()

bits = np.array(list(bitstr),dtype=np.uint8)
qrng_bytes = np.array([
    int("".join(bits[i*8:(i+1)*8].astype(str)),2)
    for i in range(len(bits)//8)
],dtype=np.uint8)

# =========================================================
# FISHER–YATES SHUFFLE (SAFE INTEGER VERSION)
# =========================================================
def fisher_yates_shuffle(indices, qrng):
    idx = indices.copy()
    q = np.tile(qrng, int(np.ceil(len(idx)/len(qrng)))).astype(np.uint32)

    for i in range(len(idx)-1, 0, -1):
        j = int(q[i]) % (i+1)
        idx[i], idx[j] = idx[j], idx[i]

    return idx

# =========================================================
# CRYPTO CLASS
# =========================================================
class RubikCubeCrypto:

    def __init__(self, image):
        self.img = image.convert("RGB")
        self.arr = np.array(self.img,dtype=np.uint8)
        self.work = self.arr.copy()
        self.m,self.n = self.arr.shape[:2]
        self.shuffled_stage = None  # To capture shuffled image

    # ---------------- KEY ----------------
    def create_key(self, qrng, rounds=5, block=8):
        q = np.tile(qrng, int(np.ceil((self.m+self.n)/len(qrng))))
        self.Kr = q[:self.m].tolist()
        self.Kc = q[self.m:self.m+self.n].tolist()
        self.rounds = rounds
        self.block = block

        with open(KEY_PATH,"wb") as f:
            f.write(base64.b64encode(json.dumps({
                "Kr": self.Kr,
                "Kc": self.Kc,
                "rounds": rounds,
                "block": block,
                "bp_index": self.bp_index
            }).encode()))

    def load_key(self):
        with open(KEY_PATH,"rb") as f:
            k = json.loads(base64.b64decode(f.read()).decode())
        self.Kr = k["Kr"]
        self.Kc = k["Kc"]
        self.rounds = k["rounds"]
        self.block = k["block"]
        self.bp_index = k["bp_index"]

    # ---------------- BLOCK PERMUTATION ----------------
    def block_permute(self, block=8):
        self.block = block
        h, w = self.m//block, self.n//block
        blocks = []

        for i in range(h):
            for j in range(w):
                blocks.append(self.work[i*block:(i+1)*block,
                                         j*block:(j+1)*block].copy())

        indices = list(range(len(blocks)))
        self.bp_index = fisher_yates_shuffle(indices, qrng_bytes)
        shuffled = [blocks[i] for i in self.bp_index]

        k = 0
        for i in range(h):
            for j in range(w):
                self.work[i*block:(i+1)*block,
                          j*block:(j+1)*block] = shuffled[k]
                k += 1

        # Capture shuffled stage
        self.shuffled_stage = self.work.copy()

    def inverse_block_permute(self):
        block = self.block
        h, w = self.m//block, self.n//block
        blocks = []

        for i in range(h):
            for j in range(w):
                blocks.append(self.work[i*block:(i+1)*block,
                                         j*block:(j+1)*block].copy())

        inv = np.argsort(self.bp_index)
        restored = [blocks[i] for i in inv]

        k = 0
        for i in range(h):
            for j in range(w):
                self.work[i*block:(i+1)*block,
                          j*block:(j+1)*block] = restored[k]
                k += 1

    # ---------------- RUBIK OPERATIONS ----------------
    def roll_rows(self,enc=True):
        d = 1 if enc else -1
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i],
                                   d*(self.Kr[i]%self.n), axis=0)

    def roll_cols(self,enc=True):
        d = 1 if enc else -1
        for j in range(self.n):
            self.work[:,j] = np.roll(self.work[:,j],
                                     d*(self.Kc[j]%self.m), axis=0)

    def xor_pixels(self):
        for i in range(self.m):
            for j in range(self.n):
                self.work[i,j] ^= (self.Kr[i]^self.Kc[j])

    # ---------------- ENCRYPT (NO INTERMEDIATE SAVES) ----------------
    def encrypt(self, use_existing_key=False, tag=""):
        self.block_permute(block=8)

        if not use_existing_key:
            self.create_key(qrng_bytes)

        for r in range(self.rounds):
            self.roll_rows(True)
            self.roll_cols(True)
            self.xor_pixels()

        return Image.fromarray(self.work)

    # ---------------- DECRYPT (NO INTERMEDIATE SAVES) ----------------
    def decrypt(self, tag=""):
        self.load_key()

        for r in range(self.rounds):
            self.xor_pixels()
            self.roll_cols(False)
            self.roll_rows(False)

        self.inverse_block_permute()

        return Image.fromarray(self.work)

# =========================================================
# LOAD IMAGE
# =========================================================
orig = Image.open(IMG_PATH)
orig_np = np.array(orig.convert("L"))

# =========================================================
# ENCRYPT
# =========================================================
crypto = RubikCubeCrypto(orig)
t0=time.time()
enc = crypto.encrypt()
t_enc=time.time()-t0

shuffled_np = np.array(Image.fromarray(crypto.shuffled_stage).convert("L"))
enc_np = np.array(enc.convert("L"))

# =========================================================
# DECRYPT
# =========================================================
t0=time.time()
dec = RubikCubeCrypto(enc).decrypt()
t_dec=time.time()-t0

dec_np = np.array(dec.convert("L"))

# =========================================================
# SAVE KEY STAGES (5 IMAGES ONLY)
# =========================================================
save_stage(orig_np, "01_original.png")
save_stage(enc_np, "02_encrypted_1.png")
save_stage(shuffled_np, "03_shuffled.png")
# Note: After encryption rounds, enc_np is the final encrypted image (Encrypted 2)
save_stage(enc_np, "04_encrypted_2_final.png")
save_stage(dec_np, "05_decrypted.png")

# =========================================================
# KEY SPACE (FOR BRUTE-FORCE ANALYSIS)
# =========================================================
M, N = orig_np.shape
key_space_bits = 8 * (M + N)

# =========================================================
# DIFFERENTIAL ATTACK (PLAINTEXT SENSITIVITY) — CORRECTED
# =========================================================

# Create modified plaintext (flip 1 bit in first pixel)
orig_diff = orig_np.copy().astype(np.int16)
orig_diff[0, 0] ^= 1  # XOR with 1 to flip LSB
orig_diff = orig_diff.astype(np.uint8)

# Encrypt original (generate key once)
crypto1 = RubikCubeCrypto(Image.fromarray(orig_np))
enc_orig = crypto1.encrypt()
enc_orig_np = np.array(enc_orig.convert("L"))

# Encrypt modified plaintext USING SAME KEY
crypto2 = RubikCubeCrypto(Image.fromarray(orig_diff))
crypto2.bp_index = crypto1.bp_index
crypto2.load_key()
enc_diff = crypto2.encrypt(use_existing_key=True)
enc_diff_np = np.array(enc_diff.convert("L"))

NPCR_val = NPCR(enc_orig_np, enc_diff_np)
UACI_val = UACI(enc_orig_np, enc_diff_np)


# =========================================================
# KEY SENSITIVITY ANALYSIS — CORRECTED
# =========================================================

# Encrypt with original key
crypto_key1 = RubikCubeCrypto(orig)
enc_key1 = np.array(crypto_key1.encrypt().convert("L"))

# Perturb QRNG key by flipping one bit
qrng_bytes_perturbed = qrng_bytes.copy()
qrng_bytes_perturbed[0] ^= 1

# Encrypt with perturbed key (reuse block permutation)
crypto_key2 = RubikCubeCrypto(orig)
crypto_key2.bp_index = crypto_key1.bp_index  # CRITICAL: reuse block permutation
crypto_key2.create_key(qrng_bytes_perturbed)
enc_key2 = np.array(crypto_key2.encrypt(use_existing_key=True).convert("L"))

# Calculate sensitivity metrics
NPCR_key = NPCR(enc_key1, enc_key2)
UACI_key = UACI(enc_key1, enc_key2)
SSIM_key = ssim_index(enc_key1, enc_key2)



# =========================================================
# SSIM
# =========================================================
SSIM_orig_dec = ssim_index(orig_np, dec_np)
SSIM_orig_enc = ssim_index(orig_np, enc_np)

# =========================================================
# CORRELATION PLOTS
# =========================================================
# Original image
correlation_plot(orig_np, "H",
                 "Horizontal Correlation (Original)",
                 "corr_orig_horizontal.png")

correlation_plot(orig_np, "V",
                 "Vertical Correlation (Original)",
                 "corr_orig_vertical.png")

correlation_plot(orig_np, "D",
                 "Diagonal Correlation (Original)",
                 "corr_orig_diagonal.png")

# Encrypted image
correlation_plot(enc_np, "H",
                 "Horizontal Correlation (Encrypted)",
                 "corr_enc_horizontal.png")

correlation_plot(enc_np, "V",
                 "Vertical Correlation (Encrypted)",
                 "corr_enc_vertical.png")

correlation_plot(enc_np, "D",
                 "Diagonal Correlation (Encrypted)",
                 "corr_enc_diagonal.png")


# =========================================================
# HISTOGRAM ANALYSIS
# =========================================================
save_histogram(orig_np,
               "Histogram of Original Image",
               "hist_original.png")

save_histogram(enc_np,
               "Histogram of Encrypted Image",
               "hist_encrypted.png")

save_histogram(dec_np,
               "Histogram of Decrypted Image",
               "hist_decrypted.png")

# =========================================================
# CORRELATION COEFFICIENTS
# =========================================================
H_o, V_o, D_o = corr_coefficients(orig_np)
H_e, V_e, D_e = corr_coefficients(enc_np)

# =========================================================
# BLOCKING ATTACK
# =========================================================
enc_block = blocking_attack(enc_np, block_ratio=0.25)
dec_block = np.array(
    RubikCubeCrypto(Image.fromarray(enc_block)).decrypt().convert("L")
)

# =========================================================
# NOISE ATTACKS
# =========================================================

# --- Salt & Pepper ---
enc_sp = salt_pepper_attack(enc_np, amount=0.05)
dec_sp = np.array(
    RubikCubeCrypto(Image.fromarray(enc_sp)).decrypt().convert("L")
)

# --- Gaussian ---
enc_gauss = gaussian_attack(enc_np, var=0.001)
dec_gauss = np.array(
    RubikCubeCrypto(Image.fromarray(enc_gauss)).decrypt().convert("L")
)

# --- QRNG-based noise ---
enc_qrng_noise = qrng_noise_attack(enc_np, qrng_bytes, strength=0.1)
dec_qrng_noise = np.array(
    RubikCubeCrypto(Image.fromarray(enc_qrng_noise)).decrypt().convert("L")
)

# =========================================================
# NOISE ATTACK METRICS
# =========================================================

# Salt & Pepper
MSE_sp  = mse(orig_np, dec_sp)
PSNR_sp = psnr(orig_np, dec_sp)
SSIM_sp = ssim_index(orig_np, dec_sp)

# Gaussian
MSE_g  = mse(orig_np, dec_gauss)
PSNR_g = psnr(orig_np, dec_gauss)
SSIM_g = ssim_index(orig_np, dec_gauss)

# QRNG noise
MSE_q  = mse(orig_np, dec_qrng_noise)
PSNR_q = psnr(orig_np, dec_qrng_noise)
SSIM_q = ssim_index(orig_np, dec_qrng_noise)


# Metrics for blocking attack
MSE_block  = mse(orig_np, dec_block)
PSNR_block = psnr(orig_np, dec_block)
SSIM_block = ssim_index(orig_np, dec_block)

log_sec, log_years = brute_force_time_estimate_log(key_space_bits)

# =========================================================
# METRICS
# =========================================================
H_orig = entropy(orig_np)
H_enc  = entropy(enc_np)
H_dec  = entropy(dec_np)

SSIM_orig_dec = ssim_index(orig_np, dec_np)
SSIM_orig_enc = ssim_index(orig_np, enc_np)

with open(os.path.join(OUT_DIR,"metrics.txt"),"w") as f:
    f.write("=== ENTROPY ANALYSIS ===\n")
    f.write(f"Initial entropy (Plain):    {H_orig:.6f}\n")
    f.write(f"Encrypted entropy (Cipher): {H_enc:.6f}\n")
    f.write(f"Final entropy (Decrypted):  {H_dec:.6f}\n\n")

    f.write("=== STRUCTURAL SIMILARITY (SSIM) ===\n")
    f.write(f"SSIM (Original vs Encrypted): {SSIM_orig_enc:.6f}\n")
    f.write(f"SSIM (Original vs Decrypted): {SSIM_orig_dec:.6f}\n\n")

    f.write("=== RECONSTRUCTION QUALITY ===\n")
    f.write(f"MSE:  {mse(orig_np,dec_np)}\n")
    f.write(f"PSNR: {psnr(orig_np,dec_np)}\n\n")

    f.write("=== TIMING ===\n")
    f.write(f"Encryption time: {t_enc}\n")
    f.write(f"Decryption time: {t_dec}\n")

    f.write("=== CORRELATION COEFFICIENTS ===\n")
    f.write("Original Image:\n")
    f.write(f"  Horizontal: {H_o}\n")
    f.write(f"  Vertical:   {V_o}\n")
    f.write(f"  Diagonal:   {D_o}\n\n")

    f.write("Encrypted Image:\n")
    f.write(f"  Horizontal: {H_e}\n")
    f.write(f"  Vertical:   {V_e}\n")
    f.write(f"  Diagonal:   {D_e}\n\n")

    f.write("=== BLOCKING ATTACK ANALYSIS ===\n")
    f.write(f"MSE (Blocking):  {MSE_block}\n")
    f.write(f"PSNR (Blocking): {PSNR_block}\n")
    f.write(f"SSIM (Blocking): {SSIM_block}\n\n")

    f.write("=== NOISE ATTACK ANALYSIS ===\n")

    f.write("Salt & Pepper Noise:\n")
    f.write(f"  MSE:  {MSE_sp}\n")
    f.write(f"  PSNR: {PSNR_sp}\n")
    f.write(f"  SSIM: {SSIM_sp}\n\n")

    f.write("Gaussian Noise:\n")
    f.write(f"  MSE:  {MSE_g}\n")
    f.write(f"  PSNR: {PSNR_g}\n")
    f.write(f"  SSIM: {SSIM_g}\n\n")

    f.write("QRNG-based Noise:\n")
    f.write(f"  MSE:  {MSE_q}\n")
    f.write(f"  PSNR: {PSNR_q}\n")
    f.write(f"  SSIM: {SSIM_q}\n\n")

    f.write("=== DIFFERENTIAL ATTACK ANALYSIS ===\n")
    f.write(f"NPCR (%): {NPCR_val}\n")
    f.write(f"UACI (%): {UACI_val}\n\n")

    f.write("=== KEY SENSITIVITY ANALYSIS ===\n")
    f.write(f"NPCR (%): {NPCR_key}\n")
    f.write(f"UACI (%): {UACI_key}\n")
    f.write(f"SSIM (Cipher vs Cipher'): {SSIM_key}\n\n")

    f.write("=== BRUTE-FORCE ATTACK ANALYSIS ===\n")
    f.write(f"Key space size: 2^{key_space_bits}\n")
    f.write("Assumed attack rate: 10^12 keys/sec\n")
    f.write(f"log10(Time in seconds): {log_sec:.2f}\n")
    f.write(f"log10(Time in years):   {log_years:.2f}\n")
    f.write("Conclusion: Brute-force attack is computationally infeasible.\n\n")
