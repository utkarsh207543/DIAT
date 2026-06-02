# 📁 NIST SP 800-22 Statistical Test Suite Hub

This directory consolidates your collection of implementations, interfaces, and ports of the **NIST SP 800-22 Randomness Testing Suite**. This suite contains 15 statistical tests designed to analyze binary sequences for cryptographic randomness.

---

## 📂 Sub-Folders & Implementations

### 1️⃣ [`c_implementation/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/c_implementation)
*   **Description:** The official C-based reference implementation of the NIST suite.
*   **Key Files:** `src/`, `include/`, `makefile`, `assess.exe`.
*   **Features:** Compiled via GCC for maximum numerical precision and lightning-fast execution on massive binary files.

### 2️⃣ [`single_file_python/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/single_file_python)
*   **Description:** A complete, 92KB single-file pure Python implementation of the suite (`main.py`).
*   **Features:** No C compiler required! Translates the interactive interactive loops of the C codebase into logical Python functions using standard math libraries. Ideal for rapid standalone tests on small streams.

### 3️⃣ [`desktop_tkinter_gui/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/desktop_tkinter_gui)
*   **Description:** A desktop graphical user interface built with Python's native `tkinter` framework.
*   **Features:**
    *   Interactive checkbox panel for selecting specific tests.
    *   Parameter entry boxes for test arguments (e.g. Block Length, Complexity).
    *   Visual "PASS/FAIL" indicators and real-time P-value calculation tables.

### 4️⃣ [`flask_web_app_v1/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/flask_web_app_v1)
*   **Description:** A basic Flask-based web application.
*   **Features:** Allows users to paste binary string streams or upload `.bin`/`.txt` files, running mathematical Python implementations of the tests in the backend and serving results in a simplified HTML report.

### 5️⃣ [`flask_web_app_v2_diat/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/flask_web_app_v2_diat)
*   **Description:** An advanced Flask web runner built specifically for your lab environment.
*   **Key Files:** `setup_and_run.py`, `nist_gui/app.py`.
*   **Features:**
    *   **Automated Compilation:** Automatically detects standard GCC installations (MinGW, Cygwin) or downloads a portable WinLibs MinGW GCC ZIP from GitHub to compile `assess.exe` on-the-fly.
    *   **ngrok Integration:** Starts a secure ngrok tunnel on port 5000 in a daemon thread so you can expose your testing dashboard securely over the web.
    *   **P-value Aggregator:** Aggregates and parses raw `finalAnalysisReport.txt` outputs from the C engine into high-level status grids.

### 6️⃣ [`react_flask_web_app_v3/`](file:///d:/Desktop/Codes/1_NIST_Statistical_Test_Suite/react_flask_web_app_v3)
*   **Description:** A modern multi-tier web application featuring a modern React frontend and a Flask REST API backend.
*   **Key Files:** `frontend/` (React/Vite/Tailwind CSS), `backend/` (Flask API).
*   **Features:** Beautiful Tailwind-styled dashboard showing visual badges, real-time file upload analytics, aggregate stream charts, and seamless CSV exports.

---

## 🚀 Getting Started

### To run the Tkinter GUI:
1.  Navigate to `desktop_tkinter_gui/`.
2.  Install dependencies: `pip install numpy scipy`
3.  Launch: `python Main.py`

### To run the Advanced DIAT Flask App:
1.  Navigate to `flask_web_app_v2_diat/`.
2.  Install requirements: `pip install flask werkzeug`
3.  Launch: `python setup_and_run.py`
4.  Open `http://localhost:5000` in your web browser. (Check port `4040` for your ngrok tunnel link).

### To run the React + Flask multi-tier web app:
1.  **Backend:**
    *   Navigate to `react_flask_web_app_v3/backend/`.
    *   Launch: `python app.py` (runs on port 5000).
2.  **Frontend:**
    *   Navigate to `react_flask_web_app_v3/frontend/`.
    *   Install dependencies: `npm install`
    *   Launch development server: `npm run dev`
    *   Open the browser link displayed in the terminal.
