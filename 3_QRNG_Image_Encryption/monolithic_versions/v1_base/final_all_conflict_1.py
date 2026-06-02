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

# =========================================================
# DECRYPT
# =========================================================
t0=time.time()
dec = RubikCubeCrypto(enc).decrypt()
t_dec=time.time()-t0

dec_np = np.array(dec.convert("L"))

# =========================================================
# METRICS
# =========================================================
with open(os.path.join(OUT_DIR,"metrics.txt"),"w") as f:
    f.write(f"MSE: {mse(orig_np,dec_np)}\n")
    f.write(f"PSNR: {psnr(orig_np,dec_np)}\n")
    f.write(f"Entropy (Encrypted): {entropy(np.array(enc.convert('L')))}\n")
    f.write(f"Encryption time: {t_enc}\n")
    f.write(f"Decryption time: {t_dec}\n")

print("✅ DONE: encryption, decryption, and all intermediate images saved.")
