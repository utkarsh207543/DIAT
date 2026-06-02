import numpy as np
import math
from skimage.metrics import structural_similarity as ssim

# =========================================================
# BASIC METRICS
# =========================================================

def mse(a, b):
    """Mean Squared Error"""
    return np.mean((a.astype(float) - b.astype(float))**2)


def psnr(a, b):
    """Peak Signal-to-Noise Ratio"""
    mse_val = mse(a, b)
    return np.inf if mse_val == 0 else 10 * np.log10(255**2 / mse_val)


def entropy(img):
    """
    Calculate Shannon entropy of image
    
    Args:
        img: Input image (numpy array)
    
    Returns:
        Entropy value
    """
    hist, _ = np.histogram(img.flatten(), 256, (0, 255))
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))


def ssim_index(a, b):
    """Structural Similarity Index"""
    return ssim(a, b, data_range=255)


# =========================================================
# DIFFERENTIAL ATTACK METRICS
# =========================================================

def NPCR(img1, img2):
    """
    Number of Pixels Change Rate
    Measures percentage of differing pixels between two images
    
    Args:
        img1, img2: Images to compare
    
    Returns:
        NPCR percentage
    """
    assert img1.shape == img2.shape

    if img1.ndim == 3:  # RGB
        diff = np.any(img1 != img2, axis=2)
    else:               # Grayscale
        diff = img1 != img2

    return np.sum(diff) / diff.size * 100


def UACI(img1, img2):
    """
    Unified Average Changing Intensity
    Measures average intensity difference between two images
    
    Args:
        img1, img2: Images to compare
    
    Returns:
        UACI percentage
    """
    assert img1.shape == img2.shape
    return np.mean(np.abs(img1.astype(np.int16) - img2.astype(np.int16))) / 255 * 100


# =========================================================
# CORRELATION ANALYSIS
# =========================================================

def corr(a, b):
    """Calculate correlation between two arrays"""
    return np.corrcoef(a.flatten(), b.flatten())[0, 1]


def corr_coefficients(img):
    """
    Calculate correlation coefficients in all directions
    
    Args:
        img: Input image
    
    Returns:
        Tuple of (horizontal, vertical, diagonal) correlations
    """
    H = corr(img[:, :-1], img[:, 1:])       # Horizontal
    V = corr(img[:-1, :], img[1:, :])       # Vertical
    D = corr(img[:-1, :-1], img[1:, 1:])    # Diagonal
    return H, V, D


# =========================================================
# KEY SPACE ANALYSIS
# =========================================================

def brute_force_time_estimate_log(key_bits, trials_per_second=1e12):
    """
    Logarithmic brute-force time estimation (overflow-safe)
    
    Args:
        key_bits: Number of key bits
        trials_per_second: Assumed attack rate
    
    Returns:
        Tuple of (log10(seconds), log10(years))
    """
    log10_total_keys = key_bits * math.log10(2)
    log10_trials_per_sec = math.log10(trials_per_second)

    log10_seconds = log10_total_keys - log10_trials_per_sec
    log10_years = log10_seconds - math.log10(60*60*24*365)

    return log10_seconds, log10_years
