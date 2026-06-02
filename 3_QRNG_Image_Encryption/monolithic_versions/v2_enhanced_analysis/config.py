import os
import sys
import argparse

# =========================================================
# PATHS CONFIGURATION
# =========================================================
BASE = os.path.dirname(os.path.abspath(__file__))

# Default paths
DEFAULT_IMG = os.path.join(BASE, "mitu.png")
DEFAULT_QRNG = os.path.join(BASE, "QRNG.txt")
DEFAULT_OUT_DIR = os.path.join(BASE, "results")
DEFAULT_KEY_PATH = os.path.join(BASE, "key.txt")

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Image Encryption & Security Analysis System")
parser.add_argument("--image", type=str, default=DEFAULT_IMG, 
                    help=f"Path to image file (default: {DEFAULT_IMG})")
parser.add_argument("--qrng", type=str, default=DEFAULT_QRNG,
                    help=f"Path to QRNG.txt file (default: {DEFAULT_QRNG})")
parser.add_argument("--output", type=str, default=DEFAULT_OUT_DIR,
                    help=f"Output directory for results (default: {DEFAULT_OUT_DIR})")

# Parse only if running as main module
args, unknown = parser.parse_known_args()

# Set paths from arguments
IMG_PATH = args.image
QRNG_PATH = args.qrng
OUT_DIR = args.output
KEY_PATH = os.path.join(OUT_DIR, "key.txt")

# Validate paths
if not os.path.exists(IMG_PATH):
    print(f"ERROR: Image file not found: {IMG_PATH}")
    print(f"Usage: python main.py --image <path> --qrng <path> --output <path>")
    sys.exit(1)

if not os.path.exists(QRNG_PATH):
    print(f"ERROR: QRNG file not found: {QRNG_PATH}")
    print(f"Usage: python main.py --image <path> --qrng <path> --output <path>")
    sys.exit(1)

# Create output directory
os.makedirs(OUT_DIR, exist_ok=True)

print(f"\n[CONFIG] Image: {IMG_PATH}")
print(f"[CONFIG] QRNG: {QRNG_PATH}")
print(f"[CONFIG] Output: {OUT_DIR}")
