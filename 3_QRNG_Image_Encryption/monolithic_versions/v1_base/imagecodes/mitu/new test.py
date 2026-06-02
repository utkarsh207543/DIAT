# =========================================================
# DIFFERENTIAL ATTACK (QRNG-STRONG, PAPER-CORRECT)
# =========================================================

# Plain image
plain1 = orig_np.copy()

# Single-pixel change (standard in literature)
plain2 = orig_np.copy()
plain2[0, 0] = (plain2[0, 0] + 1) % 256

# Encrypt both with SAME QRNG
cipher1 = QRNG_Diffusion(plain1, qrng_bytes).encrypt(rounds=2)
cipher2 = QRNG_Diffusion(plain2, qrng_bytes).encrypt(rounds=2)

# Save outputs
save_stage(cipher1, "diff_13_cipher_original.png")
save_stage(cipher2, "diff_14_cipher_modified.png")

cipher_diff = np.abs(cipher1.astype(np.int16) - cipher2.astype(np.int16)).astype(np.uint8)
save_stage(cipher_diff, "diff_15_cipher_difference.png")

# Metrics
NPCR_val = NPCR(cipher1, cipher2)
UACI_val = UACI(cipher1, cipher2)
