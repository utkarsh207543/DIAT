import numpy as np
import cv2, os, json, base64, time, math
from PIL import Image
from skimage.util import random_noise

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
def mse(a,b): return np.mean((a.astype(float)-b.astype(float))**2)
def psnr(a,b): return np.inf if mse(a,b)==0 else 10*np.log10(255**2/mse(a,b))

def entropy(img):
    hist,_ = np.histogram(img.flatten(),256,(0,255))
    p = hist/np.sum(hist)
    p = p[p>0]
    return -np.sum(p*np.log2(p))

def corr(a,b):
    return np.corrcoef(a.flatten(),b.flatten())[0,1]

# =========================================================
# LOAD QRNG BITSTRING → BYTES
# =========================================================
with open(QRNG_PATH,"r") as f:
    bitstr = f.readline().strip()

bits = np.array(list(bitstr),dtype=np.uint8)
qrng_bytes = np.array([
    int("".join(bits[i*8:(i+1)*8].astype(str)),2)
    for i in range(len(bits)//8)
],dtype=np.uint8)

# =========================================================
# QRNG RUBIK ENCRYPTION
# =========================================================
class RubikCubeCrypto:

    def __init__(self, image):
        self.img = image.convert("RGB")
        self.arr = np.array(self.img,dtype=np.uint8)
        self.work = self.arr.copy()
        self.m,self.n = self.arr.shape[:2]

    def create_key(self, qrng, rounds=5):
        q = np.tile(qrng, int(np.ceil((self.m+self.n)/len(qrng))))
        self.Kr = q[:self.m].tolist()
        self.Kc = q[self.m:self.m+self.n].tolist()
        self.rounds = rounds
        with open(KEY_PATH,"wb") as f:
            f.write(base64.b64encode(json.dumps({
                "Kr":self.Kr,"Kc":self.Kc,"rounds":rounds
            }).encode()))

    def load_key(self):
        with open(KEY_PATH,"rb") as f:
            k = json.loads(base64.b64decode(f.read()).decode())
        self.Kr,self.Kc,self.rounds = k["Kr"],k["Kc"],k["rounds"]

    def roll_rows(self,enc=True):
        d = 1 if enc else -1
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i], d*(self.Kr[i]%self.n), axis=0)

    def roll_cols(self,enc=True):
        d = 1 if enc else -1
        for j in range(self.n):
            self.work[:,j] = np.roll(self.work[:,j], d*(self.Kc[j]%self.m), axis=0)

    def xor_pixels(self):
        for i in range(self.m):
            for j in range(self.n):
                self.work[i,j] ^= (self.Kr[i]^self.Kc[j])

    def encrypt(self):
        self.create_key(qrng_bytes)
        for _ in range(self.rounds):
            self.roll_rows(True); self.roll_cols(True); self.xor_pixels()
        return Image.fromarray(self.work)

    def decrypt(self):
        self.load_key()
        for _ in range(self.rounds):
            self.xor_pixels(); self.roll_cols(False); self.roll_rows(False)
        return Image.fromarray(self.work)

# =========================================================
# LOAD IMAGE
# =========================================================
orig = Image.open(IMG_PATH)
orig_np = np.array(orig.convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"01_original.png"), orig_np)

# =========================================================
# ENCRYPT
# =========================================================
crypto = RubikCubeCrypto(orig)
t0=time.time(); enc = crypto.encrypt(); t_enc=time.time()-t0
enc_np = np.array(enc.convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"02_encrypted.png"), enc_np)

# =========================================================
# DECRYPT (NO ATTACK)
# =========================================================
t0=time.time()
dec0 = RubikCubeCrypto(enc).decrypt()
t_dec=time.time()-t0
dec0_np = np.array(dec0.convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"03_decrypted_no_attack.png"), dec0_np)

# =========================================================
# SALT & PEPPER ATTACK
# =========================================================
enc_sp = (255*random_noise(enc_np,mode='s&p',amount=0.05)).astype(np.uint8)
cv2.imwrite(os.path.join(OUT_DIR,"04_enc_sp.png"), enc_sp)
dec_sp = np.array(RubikCubeCrypto(Image.fromarray(enc_sp)).decrypt().convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"05_dec_sp.png"), dec_sp)

# =========================================================
# GAUSSIAN ATTACK
# =========================================================
enc_g = (255*random_noise(enc_np,mode='gaussian',var=0.001)).astype(np.uint8)
cv2.imwrite(os.path.join(OUT_DIR,"06_enc_gaussian.png"), enc_g)
dec_g = np.array(RubikCubeCrypto(Image.fromarray(enc_g)).decrypt().convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"07_dec_gaussian.png"), dec_g)

# =========================================================
# KEY SENSITIVITY
# =========================================================
qrng_bytes[0]^=1
enc_key = np.array(RubikCubeCrypto(orig).encrypt().convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"08_enc_key_sensitive.png"), enc_key)

# =========================================================
# DIFFERENTIAL ATTACK
# =========================================================
orig2 = orig_np.copy(); orig2[0,0]^=1
enc_diff = np.array(RubikCubeCrypto(Image.fromarray(orig2)).encrypt().convert("L"))
cv2.imwrite(os.path.join(OUT_DIR,"09_enc_differential.png"), enc_diff)

# =========================================================
# BRUTE-FORCE ATTACK ANALYSIS (KEY SPACE)
# =========================================================
M,N = orig_np.shape
key_space_bits = 8*(M+N)
key_space = 2**key_space_bits

# =========================================================
# SAVE METRICS
# =========================================================
with open(os.path.join(OUT_DIR,"metrics.txt"),"w") as f:
    f.write("=== BASELINE ===\n")
    f.write(f"MSE: {mse(orig_np,dec0_np)}\n")
    f.write(f"PSNR: {psnr(orig_np,dec0_np)}\n")
    f.write(f"Encryption time: {t_enc}\n")
    f.write(f"Decryption time: {t_dec}\n\n")

    f.write("=== ENTROPY ===\n")
    f.write(f"Original entropy:  {entropy(orig_np)}\n")
    f.write(f"Encrypted entropy: {entropy(enc_np)}\n")
    f.write(f"Decrypted entropy: {entropy(dec0_np)}\n\n")

    f.write("=== CORRELATION (ENCRYPTED) ===\n")
    f.write(f"Horizontal: {corr(enc_np[:,:-1],enc_np[:,1:])}\n")
    f.write(f"Vertical:   {corr(enc_np[:-1,:],enc_np[1:,:])}\n")
    f.write(f"Diagonal:   {corr(enc_np[:-1,:-1],enc_np[1:,1:])}\n\n")

    f.write("=== SALT & PEPPER ===\n")
    f.write(f"MSE: {mse(orig_np,dec_sp)}\n")
    f.write(f"PSNR: {psnr(orig_np,dec_sp)}\n\n")

    f.write("=== GAUSSIAN ===\n")
    f.write(f"MSE: {mse(orig_np,dec_g)}\n")
    f.write(f"PSNR: {psnr(orig_np,dec_g)}\n\n")

    f.write("=== DIFFERENTIAL ===\n")
    f.write(f"NPCR: {np.sum(enc_np!=enc_diff)/enc_np.size*100}\n")
    f.write(f"UACI: {np.mean(np.abs(enc_np-enc_diff))/255*100}\n\n")

    f.write("=== KEY SENSITIVITY ===\n")
    f.write(f"Cipher diff (%): {np.sum(enc_np!=enc_key)/enc_np.size*100}\n\n")

    f.write("=== BRUTE-FORCE ATTACK ===\n")
    f.write(f"Key space (bits): {key_space_bits}\n")
    f.write(f"Key space size: 2^{key_space_bits}\n")
    f.write("Brute-force attack is computationally infeasible.\n")

print("All results including brute-force analysis saved in /results.")
