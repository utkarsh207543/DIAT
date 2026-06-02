# 📁 QRNG Image Encryption & Security Analysis Hub

This folder contains software designed to encrypt digital images using high-entropy **Quantum Random Number Generator (QRNG)** streams. It includes tools to perform rigorous cryptographic analysis, showing that ciphertexts are secure against standard attacks.

---

## 📂 Sub-Folders & Architectures

### 1️⃣ [`modular_version_latest/`](file:///d:/Desktop/Codes/3_QRNG_Image_Encryption/modular_version_latest)
This is your **cleanest, production-ready implementation**, separated into a reusable modular package:
*   **`config.py`**: Handles paths, encryption parameters, and input configurations.
*   **`crypto_engine.py`**: The core encryption and decryption processes (AES, XOR grids, diffusion/confusion permutations).
*   **`metrics.py`**: Mathematical evaluation routines:
    *   **Shannon Entropy** calculations.
    *   **Correlation Coefficients** (horizontal, vertical, diagonal).
    *   **NPCR & UACI** calculations for differential attacks.
*   **`utils.py`**: Image file loading, data conversion, and plotting helpers.
*   **`main.py`**: The main entry script coordinating the pipeline.

### 2️⃣ [`monolithic_versions/`](file:///d:/Desktop/Codes/3_QRNG_Image_Encryption/monolithic_versions)
Contains earlier, single-script versions of the project which are useful for quick testing:
*   **`v1_base/`**: Simple script performing XOR encryption and producing standard correlation scatter plots.
*   **`v2_enhanced_analysis/`**: A larger, 21KB monolithic script (`analysis.py` & `main.py`) which includes comprehensive differential attack simulations and noise resistance benchmarks (Gaussian, Salt & Pepper noise).

---

## 📈 Cryptographic Evaluation Metrics

Your scripts calculate and output standard security metrics to validate encryption strength:

1.  **Shannon Entropy:** Evaluates pixel distribution randomness. Ideally $H \approx 8.0$ for an 8-bit encrypted image, indicating that no statistical information is leaked.
2.  **Pixel Correlation:** Measures the statistical relationship between adjacent pixels. In plain images, correlation is close to $1.0$. Your scripts confirm that encrypted ciphertexts display correlation coefficients close to $0.0$.
3.  **Differential Attack Resistance:**
    *   **NPCR (Number of Pixels Change Rate):** Measures the percentage of different pixels between two ciphertexts whose original plain images differ by exactly one pixel. Standard threshold: $\ge 99.6\%$.
    *   **UACI (Unified Average Changing Intensity):** Measures the average intensity difference between two such ciphertexts. Standard threshold: $\approx 33.4\%$.
