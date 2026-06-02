import numpy as np
import cv2, os, json, base64, time
from PIL import Image
import matplotlib.pyplot as plt
from skimage.util import random_noise
from skimage.metrics import structural_similarity as ssim


# =========================================================
# PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "mitu.png")
QRNG_PATH = os.path.join(BASE, "QRNG.txt")
KEY_PATH = os.path.join(BASE, "key.txt")
OUT_DIR = os.path.join(BASE, "results_4")
os.makedirs(OUT_DIR, exist_ok=True)

# =========================================================
# METRICS
# =========================================================

def salt_pepper_attack(img, amount=0.05):
    noisy = random_noise(img, mode='s&p', amount=amount)
    return (255 * noisy).astype(np.uint8)

def gaussian_attack(img, var=0.001):
    noisy = random_noise(img, mode='gaussian', var=var)
    return (255 * noisy).astype(np.uint8)

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

def ssim_index(a, b):
    return ssim(a, b, data_range=255)

def mse(a,b): return np.mean((a.astype(float)-b.astype(float))**2)
def psnr(a,b): return np.inf if mse(a,b)==0 else 10*np.log10(255**2/mse(a,b))

def entropy(img):
    hist,_ = np.histogram(img.flatten(),256,(0,255))
    p = hist/np.sum(hist)
    p = p[p>0]
    return -np.sum(p*np.log2(p))

def corr(a,b):
    return np.corrcoef(a.flatten(),b.flatten())[0,1]

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

    # ---------------- ENCRYPT ----------------
    def encrypt(self):
        save_stage(np.array(Image.fromarray(self.work).convert("L")),
                   "01_enc_start.png")

        self.block_permute(block=8)
        self.create_key(qrng_bytes)

        for r in range(self.rounds):
            self.roll_rows(True)
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"enc_round{r+1}_rows.png")

            self.roll_cols(True)
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"enc_round{r+1}_cols.png")

            self.xor_pixels()
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"enc_round{r+1}_xor.png")

        save_stage(np.array(Image.fromarray(self.work).convert("L")),
                   "02_encrypted_final.png")

        return Image.fromarray(self.work)

    # ---------------- DECRYPT ----------------
    def decrypt(self):
        save_stage(np.array(Image.fromarray(self.work).convert("L")),
                   "03_dec_start.png")

        self.load_key()

        for r in range(self.rounds):
            self.xor_pixels()
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"dec_round{r+1}_xor.png")

            self.roll_cols(False)
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"dec_round{r+1}_cols.png")

            self.roll_rows(False)
            save_stage(np.array(Image.fromarray(self.work).convert("L")),
                       f"dec_round{r+1}_rows.png")

        self.inverse_block_permute()

        save_stage(np.array(Image.fromarray(self.work).convert("L")),
                   "04_decrypted_final.png")

        return Image.fromarray(self.work)

# =========================================================
# LOAD IMAGE
# =========================================================
orig = Image.open(IMG_PATH)
orig_np = np.array(orig.convert("L"))
save_stage(orig_np, "01_original.png")

# =========================================================
# ENCRYPT
# =========================================================
crypto = RubikCubeCrypto(orig)
t0=time.time()
enc = crypto.encrypt()
t_enc=time.time()-t0

enc_np = np.array(enc.convert("L"))

# =========================================================
# DECRYPT
# =========================================================
t0=time.time()
dec = RubikCubeCrypto(enc).decrypt()
t_dec=time.time()-t0

dec_np = np.array(dec.convert("L"))

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
# NOISE ATTACKS
# =========================================================

# --- Salt & Pepper ---
enc_sp = salt_pepper_attack(enc_np, amount=0.05)
save_stage(enc_sp, "07_enc_salt_pepper.png")

dec_sp = np.array(
    RubikCubeCrypto(Image.fromarray(enc_sp)).decrypt().convert("L")
)
save_stage(dec_sp, "08_dec_salt_pepper.png")

# --- Gaussian ---
enc_gauss = gaussian_attack(enc_np, var=0.001)
save_stage(enc_gauss, "09_enc_gaussian.png")

dec_gauss = np.array(
    RubikCubeCrypto(Image.fromarray(enc_gauss)).decrypt().convert("L")
)
save_stage(dec_gauss, "10_dec_gaussian.png")

# --- QRNG-based noise ---
enc_qrng_noise = qrng_noise_attack(enc_np, qrng_bytes, strength=0.1)
save_stage(enc_qrng_noise, "11_enc_qrng_noise.png")

dec_qrng_noise = np.array(
    RubikCubeCrypto(Image.fromarray(enc_qrng_noise)).decrypt().convert("L")
)
save_stage(dec_qrng_noise, "12_dec_qrng_noise.png")

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
