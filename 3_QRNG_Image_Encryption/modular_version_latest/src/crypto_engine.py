import numpy as np
import json
import base64
from PIL import Image
from utils import fisher_yates_shuffle, save_stage
from config import KEY_PATH


class RubikCubeCrypto:
    def __init__(self, image):
        self.img = image.convert("RGB")
        self.arr = np.array(self.img, dtype=np.uint8)
        self.work = self.arr.copy()
        self.m, self.n = self.arr.shape[:2]
        self.bp_index = []
        self.Kr = []
        self.Kc = []
        self.rounds = 0
        self.block = 8

    # ---------------- KEY MANAGEMENT ----------------
    def create_key(self, qrng, rounds=5, block=8):
        # Generate Row/Col keys from QRNG
        q = np.tile(qrng, int(np.ceil((self.m + self.n) / len(qrng))))
        self.Kr = q[:self.m].tolist()
        self.Kc = q[self.m: self.m + self.n].tolist()
        self.rounds = rounds
        self.block = block

        # Save key to file
        key_data = {
            "Kr": self.Kr,
            "Kc": self.Kc,
            "rounds": rounds,
            "block": block,
            "bp_index": self.bp_index
        }
        with open(KEY_PATH, "wb") as f:
            f.write(base64.b64encode(json.dumps(key_data).encode()))

    def load_key(self):
        with open(KEY_PATH, "rb") as f:
            k = json.loads(base64.b64decode(f.read()).decode())
        self.Kr = k["Kr"]
        self.Kc = k["Kc"]
        self.rounds = k["rounds"]
        self.block = k["block"]
        self.bp_index = k["bp_index"]

    # ---------------- OPERATIONS ----------------
    def block_permute(self, qrng_bytes, block=8):
        self.block = block
        h, w = self.m // block, self.n // block
        blocks = []

        # Cut image into blocks
        for i in range(h):
            for j in range(w):
                blocks.append(self.work[i * block:(i + 1) * block, j * block:(j + 1) * block].copy())

        # Shuffle blocks
        indices = list(range(len(blocks)))
        self.bp_index = fisher_yates_shuffle(indices, qrng_bytes)
        shuffled = [blocks[i] for i in self.bp_index]

        # Reassemble
        k = 0
        for i in range(h):
            for j in range(w):
                self.work[i * block:(i + 1) * block, j * block:(j + 1) * block] = shuffled[k]
                k += 1

    def inverse_block_permute(self):
        block = self.block
        h, w = self.m // block, self.n // block
        blocks = []

        for i in range(h):
            for j in range(w):
                blocks.append(self.work[i * block:(i + 1) * block, j * block:(j + 1) * block].copy())

        # Unshuffle
        inv = np.argsort(self.bp_index)
        restored = [blocks[i] for i in inv]

        k = 0
        for i in range(h):
            for j in range(w):
                self.work[i * block:(i + 1) * block, j * block:(j + 1) * block] = restored[k]
                k += 1

    def roll_rows(self, enc=True):
        d = 1 if enc else -1
        for i in range(self.m):
            self.work[i] = np.roll(self.work[i], d * (self.Kr[i] % self.n), axis=0)

    def roll_cols(self, enc=True):
        d = 1 if enc else -1
        for j in range(self.n):
            self.work[:, j] = np.roll(self.work[:, j], d * (self.Kc[j] % self.m), axis=0)

    def xor_pixels(self):
        for i in range(self.m):
            for j in range(self.n):
                self.work[i, j] ^= (self.Kr[i] ^ self.Kc[j])

    # ---------------- ENCRYPT ----------------
    def encrypt(self, qrng_bytes, use_existing_key=False, tag=""):
        save_stage(np.array(Image.fromarray(self.work).convert("L")), f"{tag}01_enc_start.png")

        self.block_permute(qrng_bytes, block=8)

        if not use_existing_key:
            self.create_key(qrng_bytes)

        for r in range(self.rounds):
            self.roll_rows(True)
            self.roll_cols(True)
            self.xor_pixels()

            # Optional: Save intermediate rounds if needed
            # save_stage(np.array(Image.fromarray(self.work).convert("L")), f"{tag}enc_round{r+1}.png")

        save_stage(np.array(Image.fromarray(self.work).convert("L")), f"{tag}02_encrypted_final.png")
        return Image.fromarray(self.work)

    # ---------------- DECRYPT ----------------
    def decrypt(self, tag=""):
        save_stage(np.array(Image.fromarray(self.work).convert("L")), f"{tag}03_dec_start.png")
        self.load_key()

        for r in range(self.rounds):
            self.xor_pixels()
            self.roll_cols(False)
            self.roll_rows(False)

        self.inverse_block_permute()
        save_stage(np.array(Image.fromarray(self.work).convert("L")), f"{tag}04_decrypted_final.png")
        return Image.fromarray(self.work)