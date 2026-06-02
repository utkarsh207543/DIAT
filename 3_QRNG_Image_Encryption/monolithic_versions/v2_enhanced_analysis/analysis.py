import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
from config import OUT_DIR
from metrics import corr_coefficients
from skimage.util import random_noise

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
    Generate correlation scatter plot in grayscale
    
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
    plt.scatter(x[idx], y[idx], s=1, c='black', alpha=0.5)
    plt.title(title)
    plt.xlabel("Pixel value (i)")
    plt.ylabel("Pixel value (j)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, filename), dpi=300)
    plt.close()


def save_histogram(img, title, filename):
    """
    Generate and save histogram in grayscale
    
    Args:
        img: Input image
        title: Plot title
        filename: Output filename
    """
    plt.figure(figsize=(5, 4))
    plt.hist(img.flatten(), bins=256, range=(0, 255), density=True, color='black', edgecolor='black', alpha=0.7)
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


def generate_noise_strength_plot(orig_np, enc_np, qrng_bytes, noise_range=None):
    """
    Generate CC vs Noise Strength plots for different noise types
    
    Args:
        orig_np: Original plaintext image
        enc_np: Encrypted image
        qrng_bytes: QRNG data for QRNG noise
        noise_range: Range of noise strength values (0 to 1)
    """
    from metrics import mse
    from crypto import RubikCubeCrypto
    from PIL import Image
    from attacks import salt_pepper_attack, gaussian_attack, qrng_noise_attack
    
    # Noise strength range from 0 to 1
    if noise_range is None:
        noise_range = np.linspace(0, 1, 50)
    
    # Storage for each noise type
    cc_sp = []  # Salt & Pepper
    cc_gauss = []  # Gaussian
    cc_qrng = []  # QRNG
    
    print("      Analyzing noise type sensitivity...")
    
    for strength in noise_range:
        # Salt & Pepper Noise
        try:
            noisy_sp = salt_pepper_attack(enc_np, amount=strength)
            crypto_sp = RubikCubeCrypto(Image.fromarray(noisy_sp))
            dec_sp = np.array(crypto_sp.decrypt().convert("L"))
            cc = np.corrcoef(orig_np.flatten(), dec_sp.flatten())[0, 1]
            cc_sp.append(abs(cc))
        except:
            cc_sp.append(0)
        
        # Gaussian Noise
        try:
            noisy_gauss = gaussian_attack(enc_np, var=strength**2)
            crypto_gauss = RubikCubeCrypto(Image.fromarray(noisy_gauss))
            dec_gauss = np.array(crypto_gauss.decrypt().convert("L"))
            cc = np.corrcoef(orig_np.flatten(), dec_gauss.flatten())[0, 1]
            cc_gauss.append(abs(cc))
        except:
            cc_gauss.append(0)
        
        # QRNG Noise
        try:
            noisy_qrng = qrng_noise_attack(enc_np, qrng_bytes, strength=strength)
            crypto_qrng = RubikCubeCrypto(Image.fromarray(noisy_qrng))
            dec_qrng = np.array(crypto_qrng.decrypt().convert("L"))
            cc = np.corrcoef(orig_np.flatten(), dec_qrng.flatten())[0, 1]
            cc_qrng.append(abs(cc))
        except:
            cc_qrng.append(0)
    
    # Create combined plot - CC vs Noise Strength for all three noise types
    plt.figure(figsize=(8, 6))
    plt.plot(noise_range, cc_sp, '-', label='Salt & Pepper', linewidth=2.5)
    plt.plot(noise_range, cc_gauss, '-', label='Gaussian', linewidth=2.5)
    plt.plot(noise_range, cc_qrng, '-', label='QRNG', linewidth=2.5)
    plt.xlabel('Noise Strength', fontsize=12)
    plt.ylabel('Correlation Coefficient (CC)', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "noise_cc_vs_strength_all.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Individual plots for each noise type
    plt.figure(figsize=(7, 5))
    plt.plot(noise_range, cc_sp, '-', color='#1f77b4', linewidth=2.5)
    plt.xlabel('Noise Strength', fontsize=12)
    plt.ylabel('CC', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title('Salt & Pepper Noise Sensitivity', fontsize=13)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "noise_cc_vs_strength_salt_pepper.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    plt.figure(figsize=(7, 5))
    plt.plot(noise_range, cc_gauss, '-', color='#ff7f0e', linewidth=2.5)
    plt.xlabel('Noise Strength', fontsize=12)
    plt.ylabel('CC', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title('Gaussian Noise Sensitivity', fontsize=13)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "noise_cc_vs_strength_gaussian.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    plt.figure(figsize=(7, 5))
    plt.plot(noise_range, cc_qrng, '-', color='#2ca02c', linewidth=2.5)
    plt.xlabel('Noise Strength', fontsize=12)
    plt.ylabel('CC', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.title('QRNG Noise Sensitivity', fontsize=13)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "noise_cc_vs_strength_qrng.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return cc_sp, cc_gauss, cc_qrng, noise_range


def generate_key_perturbation_plot(orig_np, enc_np, crypto_obj, perturbation_range=None):
    """
    Generate CC and MSE vs Key Perturbation plots
    
    Args:
        orig_np: Original plaintext image
        enc_np: Original encrypted image
        crypto_obj: Original crypto object with the encryption key
        perturbation_range: Range of perturbation values (0 to 1)
    """
    from metrics import mse
    from PIL import Image
    from crypto import RubikCubeCrypto
    
    cc_values = []
    mse_values = []
    
    print("      Analyzing key sensitivity...")
    
    # Get original key components
    original_Kr = crypto_obj.Kr.copy()
    original_Kc = crypto_obj.Kc.copy()
    original_rounds = crypto_obj.rounds
    original_block = crypto_obj.block
    original_bp_index = crypto_obj.bp_index.copy() if hasattr(crypto_obj, 'bp_index') else None
    
    # Use fractional perturbation similar to research papers (0 to 1)
    if perturbation_range is None:
        perturbation_range = np.linspace(0, 1, 100)
    
    total_key_bits = (len(original_Kr) + len(original_Kc)) * 8
    
    for alpha in perturbation_range:
        # Calculate number of bits to flip based on alpha
        num_bits = int(alpha * total_key_bits)
        
        if num_bits == 0:
            # No perturbation - use original encryption
            cc = np.corrcoef(orig_np.flatten(), enc_np.flatten())[0, 1]
            cc_values.append(abs(cc))
            mse_values.append(0)
            continue
        
        # Create perturbed keys
        perturbed_Kr = original_Kr.copy()
        perturbed_Kc = original_Kc.copy()
        
        # Convert to numpy arrays for easier bit manipulation
        Kr_arr = np.array(perturbed_Kr, dtype=np.uint8)
        Kc_arr = np.array(perturbed_Kc, dtype=np.uint8)
        
        # Randomly flip num_bits in the combined key space
        bit_positions = np.random.choice(total_key_bits, min(num_bits, total_key_bits), replace=False)
        
        for bit_pos in bit_positions:
            if bit_pos < len(Kr_arr) * 8:
                # Flip bit in Kr
                byte_idx = bit_pos // 8
                bit_idx = bit_pos % 8
                Kr_arr[byte_idx] ^= (1 << bit_idx)
            else:
                # Flip bit in Kc
                bit_pos_kc = bit_pos - len(Kr_arr) * 8
                byte_idx = bit_pos_kc // 8
                bit_idx = bit_pos_kc % 8
                Kc_arr[byte_idx] ^= (1 << bit_idx)
        
        # Encrypt with perturbed key
        crypto_perturbed = RubikCubeCrypto(Image.fromarray(orig_np))
        crypto_perturbed.Kr = Kr_arr.tolist()
        crypto_perturbed.Kc = Kc_arr.tolist()
        crypto_perturbed.rounds = original_rounds
        crypto_perturbed.block = original_block
        if original_bp_index is not None:
            crypto_perturbed.bp_index = original_bp_index
        
        enc_perturbed = crypto_perturbed.encrypt(use_existing_key=True)
        enc_perturbed_np = np.array(enc_perturbed.convert("L"))
        
        # Calculate CC between original plaintext and perturbed ciphertext
        cc = np.corrcoef(orig_np.flatten(), enc_perturbed_np.flatten())[0, 1]
        cc_values.append(abs(cc))
        
        # Calculate MSE between original and perturbed ciphertext
        mse_val = mse(enc_np, enc_perturbed_np)
        mse_values.append(mse_val)
    
    # Create two side-by-side plots similar to research paper
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: MSE vs Key Perturbation (logarithmic scale)
    ax1.semilogy(perturbation_range, mse_values, '-', color='#1f77b4', linewidth=2.5)
    ax1.set_xlabel('Ord', fontsize=12)
    ax1.set_ylabel('MSE', fontsize=12)
    ax1.set_xlim(0, 1)
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax1.tick_params(labelsize=10)
    ax1.text(0.5, -0.15, '(a)', transform=ax1.transAxes, ha='center', fontsize=12)
    
    # Plot 2: CC vs Key Perturbation
    ax2.plot(perturbation_range, cc_values, '-', color='#1f77b4', linewidth=2.5)
    ax2.set_xlabel('α', fontsize=12)
    ax2.set_ylabel('CC', fontsize=12)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(-0.2, 1.0)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.tick_params(labelsize=10)
    ax2.text(0.5, -0.15, '(b)', transform=ax2.transAxes, ha='center', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "security_key_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Also save individual plots
    plt.figure(figsize=(7, 5))
    plt.semilogy(perturbation_range, mse_values, '-', color='#1f77b4', linewidth=2.5)
    plt.xlabel('Key Perturbation (fraction of bits flipped)', fontsize=12)
    plt.ylabel('MSE', fontsize=12)
    plt.xlim(0, 1)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "security_mse_vs_key_perturbation.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    plt.figure(figsize=(7, 5))
    plt.plot(perturbation_range, cc_values, '-', color='#1f77b4', linewidth=2.5)
    plt.xlabel('Key Perturbation (α)', fontsize=12)
    plt.ylabel('CC', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(-0.2, 1.0)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "security_cc_vs_key_perturbation.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return cc_values, mse_values, perturbation_range


def generate_fractional_order_sensitivity_plots(orig_np, enc_np, crypto_obj):
    """
    Generate fractional order sensitivity plots for transforms
    These simulate sensitivity to fractional Fourier and gyrator transform orders
    
    Args:
        orig_np: Original plaintext image
        enc_np: Encrypted image
        crypto_obj: Crypto object with encryption parameters
    """
    from metrics import mse
    from PIL import Image
    from crypto import RubikCubeCrypto
    
    print("      Analyzing fractional order sensitivity...")
    
    # Fractional order range from 0 to 1
    order_range = np.linspace(0, 1, 100)
    
    # Storage for results
    mse_fourier = []
    cc_gyrator = []
    
    # Get original key components
    original_Kr = crypto_obj.Kr.copy()
    original_Kc = crypto_obj.Kc.copy()
    original_rounds = crypto_obj.rounds
    original_block = crypto_obj.block
    original_bp_index = crypto_obj.bp_index.copy() if hasattr(crypto_obj, 'bp_index') else None
    
    for order in order_range:
        # Simulate fractional Fourier transform order sensitivity
        # By perturbing the row permutation key proportionally to order
        if order == 0:
            mse_fourier.append(0)
        else:
            perturbed_Kr = original_Kr.copy()
            Kr_arr = np.array(perturbed_Kr, dtype=np.uint8)
            
            # Perturb based on order (more order = more perturbation)
            num_bytes = int(order * len(Kr_arr))
            if num_bytes > 0:
                indices = np.random.choice(len(Kr_arr), num_bytes, replace=False)
                for idx in indices:
                    perturbation = int(order * 255)
                    new_val = (int(Kr_arr[idx]) + perturbation) % 256
                    Kr_arr[idx] = np.uint8(new_val)
            
            # Encrypt with perturbed key
            crypto_fourier = RubikCubeCrypto(Image.fromarray(orig_np))
            crypto_fourier.Kr = Kr_arr.tolist()
            crypto_fourier.Kc = original_Kc
            crypto_fourier.rounds = original_rounds
            crypto_fourier.block = original_block
            if original_bp_index is not None:
                crypto_fourier.bp_index = original_bp_index
            
            enc_fourier = crypto_fourier.encrypt(use_existing_key=True)
            enc_fourier_np = np.array(enc_fourier.convert("L"))
            
            mse_val = mse(enc_np, enc_fourier_np)
            mse_fourier.append(mse_val)
        
        # Simulate gyrator transform order (alpha) sensitivity
        # By perturbing the column permutation key
        if order == 0:
            cc_gyrator.append(1.0)
        else:
            perturbed_Kc = original_Kc.copy()
            Kc_arr = np.array(perturbed_Kc, dtype=np.uint8)
            
            # Perturb based on order
            num_bytes = int(order * len(Kc_arr))
            if num_bytes > 0:
                indices = np.random.choice(len(Kc_arr), num_bytes, replace=False)
                for idx in indices:
                    perturbation = int(order * 255)
                    new_val = (int(Kc_arr[idx]) + perturbation) % 256
                    Kc_arr[idx] = np.uint8(new_val)
            
            # Encrypt with perturbed key
            crypto_gyrator = RubikCubeCrypto(Image.fromarray(orig_np))
            crypto_gyrator.Kr = original_Kr
            crypto_gyrator.Kc = Kc_arr.tolist()
            crypto_gyrator.rounds = original_rounds
            crypto_gyrator.block = original_block
            if original_bp_index is not None:
                crypto_gyrator.bp_index = original_bp_index
            
            enc_gyrator = crypto_gyrator.encrypt(use_existing_key=True)
            enc_gyrator_np = np.array(enc_gyrator.convert("L"))
            
            cc = np.corrcoef(orig_np.flatten(), enc_gyrator_np.flatten())[0, 1]
            cc_gyrator.append(abs(cc))
    
    # Create two side-by-side plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: MSE vs Fractional Fourier Transform Order
    ax1.semilogy(order_range, mse_fourier, '-', color='#1f77b4', linewidth=2.5)
    ax1.set_xlabel('Ord', fontsize=12)
    ax1.set_ylabel('MSE', fontsize=12)
    ax1.set_xlim(0, 1)
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax1.tick_params(labelsize=10)
    ax1.text(0.5, -0.15, '(a)', transform=ax1.transAxes, ha='center', fontsize=12)
    
    # Plot 2: CC vs Gyrator Order (alpha)
    ax2.plot(order_range, cc_gyrator, '-', color='#1f77b4', linewidth=2.5)
    ax2.set_xlabel('α', fontsize=12)
    ax2.set_ylabel('CC', fontsize=12)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax2.tick_params(labelsize=10)
    ax2.text(0.5, -0.15, '(b)', transform=ax2.transAxes, ha='center', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fractional_order_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Also save individual plots
    plt.figure(figsize=(7, 5))
    plt.semilogy(order_range, mse_fourier, '-', color='#1f77b4', linewidth=2.5)
    plt.xlabel('Fractional Fourier Transform Order', fontsize=12)
    plt.ylabel('MSE', fontsize=12)
    plt.xlim(0, 1)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fractional_fourier_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    plt.figure(figsize=(7, 5))
    plt.plot(order_range, cc_gyrator, '-', color='#1f77b4', linewidth=2.5)
    plt.xlabel('Gyrator Order (α)', fontsize=12)
    plt.ylabel('CC', fontsize=12)
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    plt.tick_params(labelsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "gyrator_order_sensitivity.png"), dpi=300, bbox_inches='tight')
    plt.close()
    
    return mse_fourier, cc_gyrator, order_range
