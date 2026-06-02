import os

# =========================================================
# PATH CONFIGURATION
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Input Files
IMG_PATH = os.path.join(BASE_DIR, "mitu.png")
QRNG_PATH = os.path.join(BASE_DIR, "QRNG.txt")

# Output Directories & Files
OUT_DIR = os.path.join(BASE_DIR, "results")
KEY_PATH = os.path.join(BASE_DIR, "key.txt")
METRICS_FILE = os.path.join(OUT_DIR, "metrics.txt")

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)

# Crypto Constants
ROUNDS = 5
BLOCK_SIZE = 8