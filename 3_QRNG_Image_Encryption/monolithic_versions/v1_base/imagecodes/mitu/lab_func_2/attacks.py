import numpy as np
from skimage.util import random_noise
from PIL import Image
from crypto import RubikCubeCrypto

# =========================================================
# ATTACK FUNCTIONS
# =========================================================

def blocking_attack(img, block_ratio=0.2):
    """
    Zero out a central block of the encrypted image
    
    Args:
        img: Input image (numpy array)
        block_ratio: Fraction of image size to block
    
    Returns:
        Image with central block zeroed
    """
    attacked = img.copy()
    h, w = img.shape

    bh = int(h * block_ratio)
    bw = int(w * block_ratio)

    y0 = (h - bh) // 2
    x0 = (w - bw) // 2

    attacked[y0:y0+bh, x0:x0+bw] = 0
    return attacked


def salt_pepper_attack(img, amount=0.05):
    """
    Add salt and pepper noise to image
    
    Args:
        img: Input image (numpy array)
        amount: Fraction of pixels to corrupt
    
    Returns:
        Noisy image
    """
    noisy = random_noise(img, mode='s&p', amount=amount)
    return (255 * noisy).astype(np.uint8)


def gaussian_attack(img, var=0.001):
    """
    Add Gaussian noise to image
    
    Args:
        img: Input image (numpy array)
        var: Variance of Gaussian noise
    
    Returns:
        Noisy image
    """
    noisy = random_noise(img, mode='gaussian', var=var)
    return (255 * noisy).astype(np.uint8)


def qrng_noise_attack(img, qrng, strength=0.1):
    """
    QRNG-driven noise attack using hardware entropy
    
    Args:
        img: Input image (numpy array)
        qrng: QRNG bytes array
        strength: Fraction of max intensity (0-1)
    
    Returns:
        Noisy image
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


# =========================================================
# ATTACK ORCHESTRATION
# =========================================================

def perform_blocking_attack(enc_np):
    """
    Perform blocking attack and decrypt
    
    Returns:
        Tuple of (attacked_encrypted, decrypted)
    """
    enc_block = blocking_attack(enc_np, block_ratio=0.25)
    dec_block = np.array(
        RubikCubeCrypto(Image.fromarray(enc_block)).decrypt().convert("L")
    )
    return enc_block, dec_block


def perform_salt_pepper_attack(enc_np):
    """
    Perform salt & pepper attack and decrypt
    
    Returns:
        Tuple of (attacked_encrypted, decrypted)
    """
    enc_sp = salt_pepper_attack(enc_np, amount=0.05)
    dec_sp = np.array(
        RubikCubeCrypto(Image.fromarray(enc_sp)).decrypt().convert("L")
    )
    return enc_sp, dec_sp


def perform_gaussian_attack(enc_np):
    """
    Perform Gaussian noise attack and decrypt
    
    Returns:
        Tuple of (attacked_encrypted, decrypted)
    """
    enc_gauss = gaussian_attack(enc_np, var=0.001)
    dec_gauss = np.array(
        RubikCubeCrypto(Image.fromarray(enc_gauss)).decrypt().convert("L")
    )
    return enc_gauss, dec_gauss


def perform_qrng_noise_attack(enc_np, qrng_bytes):
    """
    Perform QRNG-based noise attack and decrypt
    
    Returns:
        Tuple of (attacked_encrypted, decrypted)
    """
    enc_qrng_noise = qrng_noise_attack(enc_np, qrng_bytes, strength=0.1)
    dec_qrng_noise = np.array(
        RubikCubeCrypto(Image.fromarray(enc_qrng_noise)).decrypt().convert("L")
    )
    return enc_qrng_noise, dec_qrng_noise
