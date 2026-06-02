import numpy as np
import cv2, os, json, base64, time
from PIL import Image
from skimage.util import random_noise

# =========================================================
# PATHS
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE, "mitu.png")
QRNG_PATH = os.path.join(BASE, "QRNG.txt")
KEY_PATH = os.path.join(BASE, "key.txt")

# =========================================================
# LOAD QRNG BITSTRING → BYTES
# =========================================================
with open(QRNG_PATH, "r") as f:
    bitstr = f.readline().strip()

bits = np.array(list(bitstr), dtype=np.uint8)
num_bytes = len(bits) // 8

qrng_bytes = np.array([
    int("".join(bits[i*8:(i+1)*8].astype(str)), 2)
    for i in range(num_bytes)
], dtype=np.uint8)

# =========================================================
# METRICS
# =========================================================
def mse(a,b): return np.mean((a.astype(float)-b.astype(float))**2)
def psnr(a,b): return np.inf if mse(a,b)==0 else 10*np.log10(255**2/mse(a,b))

# =========================================================
# RUBIK CUBE CRYPTO (QRNG)
# =========================================================
class RubikCubeCrypto:

    def __init__(self, image):
        self.img = image.convert("RGB")
        self.arr = np.array(self.img, dtype=np.uint8)
        self.work = self.arr.copy()
        self.m, self.n = self.arr.shape[:2]

    def create_key(self, qrng, rounds=5):
        needed = self.m + self.n
        qrng = np.tile(qrng, int(np.ceil(needed / len(qrng))))
        self.Kr = qrng[:self.m].tolist()
        self.Kc = qrng[self.m:self.m+self.n].tolist()
        self.rounds = rounds
        with open(KEY_PATH, "wb") as f:
            f.write(base64.b64encode(json.dumps({
                "Kr": self.Kr, "Kc": self.Kc, "rounds": rounds
            }).encode()))

    def load_key(self):
        with open(KEY_PATH, "rb") as f:
            k = json.loads(base64.b64decode(f.read()).decode())
        self.Kr, self.Kc, self.rounds = k["Kr"], k["Kc"], k["rounds"]

    def roll_rows(self, enc=True):
        d = 1 if enc else -1
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i], d*(self.Kr[i] % self.n), axis=0)

    def roll_cols(self, enc=True):
        d = 1 if enc else -1
        for j in range(self.n):
            self.work[:,j] = np.roll(self.work[:,j], d*(self.Kc[j] % self.m), axis=0)

    def xor_pixels(self):
        for i in range(self.m):
            for j in range(self.n):
                self.work[i,j] ^= (self.Kr[i] ^ self.Kc[j])

    def encrypt(self):
        self.create_key(qrng_bytes)
        for _ in range(self.rounds):
            self.roll_rows(True)
            self.roll_cols(True)
            self.xor_pixels()
        return Image.fromarray(self.work)

    def decrypt(self):
        self.load_key()
        for _ in range(self.rounds):
            self.xor_pixels()
            self.roll_cols(False)
            self.roll_rows(False)
        return Image.fromarray(self.work)

# =========================================================
# LOAD IMAGE
# =========================================================
orig = Image.open(IMG_PATH)
orig_np = np.array(orig.convert("L"))

# =========================================================
# BASELINE ENCRYPTION
# =========================================================
crypto = RubikCubeCrypto(orig)
t0 = time.time()
enc_img = crypto.encrypt()
t_enc = time.time() - t0

enc_np = np.array(enc_img.convert("L"))
cv2.imwrite("enc.png", enc_np)

# =========================================================
# BASELINE DECRYPTION (NO ATTACK)
# =========================================================
t0 = time.time()
dec_base = RubikCubeCrypto(enc_img).decrypt()
t_dec = time.time() - t0

dec_base_np = np.array(dec_base.convert("L"))
cv2.imwrite("dec_no_attack.png", dec_base_np)

print("\n=== BASELINE ===")
print("MSE:", mse(orig_np, dec_base_np))
print("PSNR:", psnr(orig_np, dec_base_np))
print("Enc time:", t_enc, "Dec time:", t_dec)

# =========================================================
# SALT & PEPPER NOISE ATTACK
# =========================================================
enc_sp = random_noise(enc_np, mode='s&p', amount=0.05)
enc_sp = (255*enc_sp).astype(np.uint8)
cv2.imwrite("enc_sp.png", enc_sp)

dec_sp = np.array(RubikCubeCrypto(Image.fromarray(enc_sp)).decrypt().convert("L"))
cv2.imwrite("dec_sp.png", dec_sp)

print("\n=== SALT & PEPPER ATTACK ===")
print("MSE:", mse(orig_np, dec_sp))
print("PSNR:", psnr(orig_np, dec_sp))

# =========================================================
# GAUSSIAN NOISE ATTACK
# =========================================================
enc_g = random_noise(enc_np, mode='gaussian', var=0.001)
enc_g = (255*enc_g).astype(np.uint8)
cv2.imwrite("enc_gaussian.png", enc_g)

dec_g = np.array(RubikCubeCrypto(Image.fromarray(enc_g)).decrypt().convert("L"))
cv2.imwrite("dec_gaussian.png", dec_g)

print("\n=== GAUSSIAN NOISE ATTACK ===")
print("MSE:", mse(orig_np, dec_g))
print("PSNR:", psnr(orig_np, dec_g))

# =========================================================
# DIFFERENTIAL ATTACK (NPCR / UACI)
# =========================================================
orig2 = orig_np.copy()
orig2[0,0] ^= 1

enc2 = np.array(RubikCubeCrypto(Image.fromarray(orig2)).encrypt().convert("L"))

NPCR = np.sum(enc_np != enc2) / enc_np.size * 100
UACI = np.mean(np.abs(enc_np - enc2)) / 255 * 100

print("\n=== DIFFERENTIAL ATTACK ===")
print("NPCR:", NPCR)
print("UACI:", UACI)

# =========================================================
# KEY SENSITIVITY ATTACK
# =========================================================
qrng_bytes[0] ^= 1
enc_key = np.array(RubikCubeCrypto(orig).encrypt().convert("L"))

key_diff = np.sum(enc_np != enc_key) / enc_np.size * 100
cv2.imwrite("enc_key_sensitive.png", enc_key)

print("\n=== KEY SENSITIVITY ===")
print("Cipher difference (%):", key_diff)

print("\nAll attacks completed. Images saved.")
