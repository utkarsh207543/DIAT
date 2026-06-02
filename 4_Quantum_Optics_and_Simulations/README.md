# 📁 Quantum Optics & Theoretical Physics Simulations Hub

Welcome to your physics simulation and laboratory experimental processing directory. This hub houses your models for **Fiber Lasers**, **Hanbury Brown-Twiss Interferometry**, **Quantum Entanglement correlations**, and **Rogue Wave statistical analyses**.

---

## 📂 Sub-Folders & Physical Models

### 1️⃣ [`fiber_laser_simulation/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/fiber_laser_simulation)
*   **Physics:** Simulates nonlinear pulse propagation inside fiber cavity systems governed by the **Nonlinear Schrödinger Equation (NLSE)**.
*   **Key Files:**
    *   **Solvers:** `propagation_solver.py`, `fivercudasim.py` (GPU-accelerated NLSE).
    *   **Components:** `components.py` (gain saturation, filters, couplers, saturable absorbers).
    *   **MATLAB Models:** Complete set of `.m` counterparts for cross-verifying cavity dynamics.
*   **Usage:** Models soliton formation, dissipative solitons, and spectral breathing inside mode-locked laser cavity configurations.

### 2️⃣ [`hbt_interferometer_g2/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/hbt_interferometer_g2)
*   **Physics:** Computes the second-order temporal correlation function $g^{(2)}(\tau)$ using timetags logged from a **Moku Time-Frequency Analyzer**.
*   **Key Files:** `g2_from_timtags.py`, `simulate_hbt.py`, `batch_g2.py`.
*   **Data Separation:** All heavy timetag datasets (CSV, NPY files up to 2.5GB) are isolated inside `hbt_interferometer_g2/data/` to keep filesystem indexing fast.
*   **Interpretation:** Allows you to verify whether your source exhibits photon bunching ($g^{(2)}(0) > 1$ for chaotic light), antibunching ($g^{(2)}(0) < 1$ for single photons), or coherent statistics ($g^{(2)}(0) \approx 1$).

### 3️⃣ [`spdc_and_quantum_key/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/spdc_and_quantum_key)
*   **Physics:** Simulates **Spontaneous Parametric Down-Conversion (SPDC)** in nonlinear crystals (like Beta Barium Borate - BBO) to generate entangled photon pairs for Quantum Key Distribution (QKD).
*   **Key Files:** `BBO_pol.py`, `main.py` (QWL analysis), `xor.py`.
*   **Features:** Evaluates key generation rates, polarization entanglement correlations, and quantum phase adjustments.

### 4️⃣ [`rogue_wave_qrng/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/rogue_wave_qrng)
*   **Physics:** Analyzes high-power optical rogue wave events in laser cavities to extract physical entropy for QRNG pipelines.
*   **Key Files:** `RWanalysfromcsv.py`, `batch_rogue_qrng.py`, `rogue_events.csv`.
*   **Features:** Fits experimental intensity data, plots Complementary Cumulative Distribution Functions (CCDF) to isolate heavy-tailed rogue distributions, and maps threshold events into binary keys.

### 5️⃣ [`ghost_imaging/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/ghost_imaging)
*   **Physics:** Processes experimental measurements of correlated intensity fluctuations to reconstruct digital images via **Ghost Imaging** algorithms.
*   **Key Files:** `test.py`, `test.csv` (imaging dataset).

### 6️⃣ [`qiskit_simulations/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/qiskit_simulations)
*   **Description:** Holds quantum circuit configurations.
*   **Subfolders:**
    *   `custom_qiskit_experiments/`: Custom circuit models.
    *   `qiskit-aer/`: The complete cloned Qiskit Aer high-performance simulator backend repository.

### 7️⃣ [`practice_and_lab_scratchcodes/`](file:///d:/Desktop/Codes/4_Quantum_Optics_and_Simulations/practice_and_lab_scratchcodes)
*   **Description:** A clean scratchpad for general Python tutorials, basic calculator GUIs, and quick diagnostic scripts (such as `xrd_origin.py` or simple thread tests).
