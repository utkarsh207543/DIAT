# 🌌 Advanced Quantum Optics, QRNG & Cryptography Lab Suite

Welcome to your consolidated, premium laboratory workspace. This repository contains your research, simulations, and production code for **Quantum Optics**, **Quantum Random Number Generation (QRNG)**, and **Cryptographic Randomness Testing**.

All codes have been organized into a professional, version-controlled taxonomy to isolate large laboratory datasets, resolve redundancies, cluster developmental versions, and provide clean entry points.

---

## 📂 Consolidated Taxonomy & Architecture

The workspace is structured into **four primary directories**, each representing a dedicated research and development domain:

```
d:\Desktop\Codes\
├── 📁 1_NIST_Statistical_Test_Suite/        # Randomness testing interfaces and ports
├── 📁 2_QRNG_Post_Processing_and_Pipelines/ # Serial loggers, debiasing, and extractors
├── 📁 3_QRNG_Image_Encryption/              # QRNG-based image encryption & security analysis
└── 📁 4_Quantum_Optics_and_Simulations/     # Physics models, HBT interferometer & lasers
```

---

## 🔍 Directory Summaries & Entry Points

### 1️⃣ [1_NIST_Statistical_Test_Suite](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite)
This folder houses all implementations and user interfaces of the **NIST SP 800-22 Statistical Test Suite**, used to evaluate the cryptographic quality of random number generators.
*   **`c_implementation/`**: The original, official NIST C-code codebase with optimized compile configurations.
*   **`single_file_python/`**: A standalone, lightweight 92KB pure Python port of all 15 NIST tests.
*   **`desktop_tkinter_gui/`**: An interactive Python Tkinter desktop dashboard for launching tests mathematically in Python.
*   **`flask_web_app_v1/`**: A clean, basic Flask web interface for managing bitstream files.
*   **`flask_web_app_v2_diat/`**: An advanced Flask runner featuring portable GCC compilation triggers and ngrok secure tunnelling.
*   **`react_flask_web_app_v3/`**: A modern multi-tier web application featuring a React (Vite/Tailwind) dashboard and a Flask API backend.

### 2️⃣ [2_QRNG_Post_Processing_and_Pipelines](file:///d:/Desktop/Codes/2_QRNG_Post_Processing_and_Pipelines)
Consolidates post-processing tools that turn raw quantum timetags into cryptographically secure, unbiased random bits.
*   **`privacy_amplification_versions/`**: Chronological versions of your extraction pipeline:
    *   `v1_base`: Basic Von Neumann debiasing.
    *   `v2_entropy_amp`: Introduces entropy amplification.
    *   `v3_entropy_amp_optimized`: Optimizes processing speed.
    *   `v4_fast_leftover`: Implements the fast leftover hash lemma (Toeplitz matrix hashing).
    *   `v5_unicode_fix_latest`: Resolves unicode string encoding issues (your primary production version).
*   **`paper_ready_pipelines/`**: Fully integrated RCI and Quantum29 paper-ready evaluation pipelines.
*   **`serial_logger/`**: Serial readers and dataloggers for logging live QRNG outputs from hardware interfaces.
*   **`beacon_and_timetags/`**: Timetag-to-bit parsers and beacon epoch generation scripts.

### 3️⃣ [3_QRNG_Image_Encryption](file:///d:/Desktop/Codes/3_QRNG_Image_Encryption)
Contains software for encrypting images using QRNG streams and analyzing the ciphertexts against differential attacks.
*   **`modular_version_latest/`**: A beautifully clean, modularized production version with separate files for `config`, `crypto_engine`, `metrics`, and `utils`.
*   **`monolithic_versions/`**: Traditional single-script versions:
    *   `v1_base`: The base encryption and correlation dashboard.
    *   `v2_enhanced_analysis`: Advanced version including extensive NPCR, UACI, and differential attack simulations.

### 4️⃣ [4_Quantum_Optics_and_Simulations](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations)
Consolidates all laboratory experimental code and theoretical physics simulation models.
*   **`fiber_laser_simulation/`**: Split-Step Fourier solvers (SSFM) in MATLAB and Python, simulating nonlinear pulse propagation.
*   **`hbt_interferometer_g2/`**: Hanbury Brown-Twiss $g^{(2)}(\tau)$ second-order temporal correlation calculators.
    *   *Note: All massive CSV, NPY, and binary timetag datasets are isolated under `hbt_interferometer_g2/data/`.*
*   **`spdc_and_quantum_key/`**: Theoretical phase adjustments, Spontaneous Parametric Down-Conversion (SPDC) crystals, and Quantum Key Distribution (QKD) rate simulators.
*   **`rogue_wave_qrng/`**: Intensity thresholding and CCDF rogue-wave-based QRNG statistics.
*   **`ghost_imaging/`**: Mathematical solvers and data for Ghost Imaging.
*   **`qiskit_simulations/`**: Custom Qiskit quantum computing codes and the cloned `qiskit-aer` repository.
*   **`practice_and_lab_scratchcodes/`**: General tutorial scripts and quick scratchpads.

---

## 🛠️ Unified Development Guidelines

1.  **Virtual Environments:** To keep your workspace lightweight, duplicate virtual environments (`venv`, `.venv`) have been removed. You can set up a single, clean virtual environment inside any of the four primary folders using:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate     # On Windows
    ```
2.  **Dataset Isolation:** Never commit or upload large binary/CSV files directly to code repositories. Keep all experimental datasets under their respective `data/` directories to maintain fast filesystem performance.
3.  **Cross-Project Work:** If you need to integrate QRNG bits directly with Image Encryption or NIST testing, simply reference paths across the top-level directories.

---
*Organized & Documented in June 2026 for Defence Institute of Advanced Technology (DIAT) & DRDO Quantum Research Initiatives.*
