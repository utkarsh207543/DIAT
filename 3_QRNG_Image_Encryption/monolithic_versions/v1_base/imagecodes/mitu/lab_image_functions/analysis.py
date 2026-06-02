import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from config import OUT_DIR
from metrics import corr_coefficients

# =========================================================
# IMAGE SAVING
# =========================================================

def save_stage(arr, name):
    """Save numpy array as image"""
    cv2.imwrite(os.path.join(OUT_DIR, name), arr)


# =========================================================
# VISUALIZATION & PLOTTING
# =========================================================

def correlation_plot(img, direction, title, filename, samples=5000):
    """
    Generate correlation scatter plot
    
    Args:
        img: Input image
        direction: 'H' (horizontal), 'V' (vertical), or 'D' (diagonal)
        title: Plot title
        filename: Output filename
        samples: Number of points to plot
    """
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

    plt.figure(figsize=(4, 4))
    plt.scatter(x[idx], y[idx], s=1)
    plt.title(title)
    plt.xlabel("Pixel value (i)")
    plt.ylabel("Pixel value (j)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


def save_histogram(img, title, filename):
    """
    Generate and save histogram
    
    Args:
        img: Input image
        title: Plot title
        filename: Output filename
    """
    plt.figure(figsize=(5, 4))
    plt.hist(img.flatten(), bins=256, range=(0, 255), density=True)
    plt.title(title)
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Probability")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


# =========================================================
# ANALYSIS FUNCTIONS
# =========================================================

def generate_key_stage_images(orig_np, enc_np, shuffled_np, dec_np):
    """
    Save the 5 key encryption stages
    
    Args:
        orig_np: Original image
        enc_np: Encrypted image
        shuffled_np: Shuffled intermediate stage
        dec_np: Decrypted image
    """
    save_stage(orig_np, "01_original.png")
    save_stage(enc_np, "02_encrypted_1.png")
    save_stage(shuffled_np, "03_shuffled.png")
    save_stage(enc_np, "04_encrypted_2_final.png")
    save_stage(dec_np, "05_decrypted.png")


def generate_correlation_analysis(orig_np, enc_np):
    """
    Generate correlation plots for original and encrypted images
    
    Args:
        orig_np: Original image
        enc_np: Encrypted image
    """
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


def generate_histogram_analysis(orig_np, enc_np, dec_np):
    """
    Generate histogram plots for images
    
    Args:
        orig_np: Original image
        enc_np: Encrypted image
        dec_np: Decrypted image
    """
    save_histogram(orig_np,
                   "Histogram of Original Image",
                   "hist_original.png")

    save_histogram(enc_np,
                   "Histogram of Encrypted Image",
                   "hist_encrypted.png")

    save_histogram(dec_np,
                   "Histogram of Decrypted Image",
                   "hist_decrypted.png")


def get_correlation_coefficients(orig_np, enc_np):
    """
    Get correlation coefficients for original and encrypted images
    
    Args:
        orig_np: Original image
        enc_np: Encrypted image
    
    Returns:
        Dict with correlation data
    """
    H_o, V_o, D_o = corr_coefficients(orig_np)
    H_e, V_e, D_e = corr_coefficients(enc_np)
    
    return {
        'orig': {'H': H_o, 'V': V_o, 'D': D_o},
        'enc': {'H': H_e, 'V': V_e, 'D': D_e}
    }
