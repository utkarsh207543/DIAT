import numpy as np
import json
import base64
from PIL import Image
from config import KEY_PATH
from qrng_utils import fisher_yates_shuffle, qrng_bytes

# =========================================================
# RUBIK CUBE CRYPTO CLASS
# =========================================================
class RubikCubeCrypto:
    """
    Image encryption using Rubik's Cube inspired operations:
    1. Block permutation (shuffling)
    2. Row shifts
    3. Column shifts
    4. XOR pixel operations
    """

    def __init__(self, image):
        """
        Initialize with PIL Image
        
        Args:
            image: PIL Image object
        """
        self.img = image.convert("RGB")
        self.arr = np.array(self.img, dtype=np.uint8)
        self.work = self.arr.copy()
        self.m, self.n = self.arr.shape[:2]
        self.shuffled_stage = None  # To capture shuffled image

    # ============ KEY MANAGEMENT ============
    def create_key(self, qrng, rounds=5, block=8):
        """
        Create and save encryption key from QRNG
        
        Args:
            qrng: QRNG bytes array
            rounds: Number of encryption rounds
            block: Block size for permutation
        """
        q = np.tile(qrng, int(np.ceil((self.m+self.n)/len(qrng))))
        self.Kr = q[:self.m].tolist()
        self.Kc = q[self.m:self.m+self.n].tolist()
        self.rounds = rounds
        self.block = block

        with open(KEY_PATH, "wb") as f:
            f.write(base64.b64encode(json.dumps({
                "Kr": self.Kr,
                "Kc": self.Kc,
                "rounds": rounds,
                "block": block,
                "bp_index": self.bp_index
            }).encode()))

    def load_key(self):
        """Load encryption key from file"""
        with open(KEY_PATH, "rb") as f:
            k = json.loads(base64.b64decode(f.read()).decode())
        self.Kr = k["Kr"]
        self.Kc = k["Kc"]
        self.rounds = k["rounds"]
        self.block = k["block"]
        self.bp_index = k["bp_index"]

    # ============ BLOCK PERMUTATION ============
    def block_permute(self, block=8):
        """
        Permute image blocks using Fisher-Yates shuffle
        
        Args:
            block: Block size for permutation
        """
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
        """Reverse block permutation during decryption"""
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

    # ============ RUBIK OPERATIONS ============
    def roll_rows(self, enc=True):
        """
        Shift pixels in each row
        
        Args:
            enc: True for encryption, False for decryption
        """
        d = 1 if enc else -1
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i],
                                   d*(self.Kr[i]%self.n), axis=0)

    def roll_cols(self, enc=True):
        """
        Shift pixels in each column
        
        Args:
            enc: True for encryption, False for decryption
        """
        d = 1 if enc else -1
        for j in range(self.n):
            self.work[:, j] = np.roll(self.work[:, j],
                                      d*(self.Kc[j]%self.m), axis=0)

    def xor_pixels(self):
        """XOR each pixel with key material"""
        for i in range(self.m):
            for j in range(self.n):
                self.work[i, j] ^= (self.Kr[i]^self.Kc[j])

    # ============ ENCRYPT/DECRYPT ============
    def encrypt(self, use_existing_key=False, skip_block_permute=False):
        """
        Encrypt image using Rubik's cube-like operations
        
        Args:
            use_existing_key: If True, use loaded key instead of creating new one
            skip_block_permute: If True, skip block permutation (for differential attacks)
        
        Returns:
            Encrypted PIL Image
        """
        # Only perform block permutation if not skipping (for differential attack)
        if not skip_block_permute:
            self.block_permute(block=8)

        if not use_existing_key:
            self.create_key(qrng_bytes)

        for r in range(self.rounds):
            self.roll_rows(True)
            self.roll_cols(True)
            self.xor_pixels()

        return Image.fromarray(self.work)

    def decrypt(self):
        """
        Decrypt image by reversing operations
        
        Returns:
            Decrypted PIL Image
        """
        self.load_key()

        for r in range(self.rounds):
            self.xor_pixels()
            self.roll_cols(False)
            self.roll_rows(False)

        self.inverse_block_permute()

        return Image.fromarray(self.work)
