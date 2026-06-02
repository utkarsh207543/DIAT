import os
import subprocess
import sys
import threading
import time
import webbrowser
import shutil
import zipfile
import urllib.request

def check_compiler(name):
    """Checks if a compiler is available in PATH."""
    try:
        subprocess.run([name, '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_compiler():
    """Downloads and sets up a portable MinGW compiler."""
    print("[*] Attempting to download portable MinGW compiler...")
    url = "https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0-16.0.6-11.0.1-msvcrt-r1/winlibs-x86_64-posix-seh-gcc-13.2.0-mingw-w64msvcrt-11.0.1-r1.zip"
    
    local_zip = os.path.join(os.path.dirname(__file__), "mingw.zip")
    extract_dir = os.path.join(os.path.dirname(__file__), "mingw_portable")
    
    if os.path.exists(extract_dir):
        # Already extracted? Check if gcc is there
        gcc_path = os.path.join(extract_dir, "mingw64", "bin", "gcc.exe")
        if os.path.exists(gcc_path):
            print("[*] Portable compiler already exists.")
            return gcc_path

    try:
        print(f"[*] Downloading from {url}...")
        urllib.request.urlretrieve(url, local_zip)
        print("[*] Download complete. Extracting...")
        
        with zipfile.ZipFile(local_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        print("[*] Extraction complete.")
        os.remove(local_zip)
        
        return os.path.join(extract_dir, "mingw64", "bin", "gcc.exe")
        
    except Exception as e:
        print(f"[!] automated compiler setup failed: {e}")
        return None

def compile_assess():
    """Attempts to compile the assess executable if it doesn't exist."""
    nist_dir = os.path.join(os.path.dirname(__file__), 'nist')
    assess_exe = os.path.join(nist_dir, 'assess.exe')

    if os.path.exists(assess_exe):
        print("[*] assess.exe already exists.")
        return True

    print("[!] assess.exe not found. Attempting to compile...")

    # Check for Cygwin
    cygwin_bin = r"C:\cygwin64\bin"
    if os.path.exists(os.path.join(cygwin_bin, "gcc.exe")):
        print(f"[*] Found Cygwin GCC in {cygwin_bin}. Adding to PATH...")
        os.environ["PATH"] += os.pathsep + cygwin_bin

    # Check for MinGW (Common Paths)
    mingw_paths = [r"C:\mingw64\bin", r"C:\MinGW\bin"]
    for path in mingw_paths:
        if os.path.exists(os.path.join(path, "gcc.exe")):
             # Verify it's not broken (check for cc1.exe recursively nearby or assume user fixed it)
             # But let's just try to add it.
             print(f"[*] Found MinGW GCC in {path}. Adding to PATH...")
             os.environ["PATH"] += os.pathsep + path
             break
    
    # Check for compilers before running batch to give better feedback
    has_gcc = check_compiler('gcc')
    has_cl = check_compiler('cl')
    
    if not has_gcc and not has_cl:
         print("\n[!] No C compiler found. Checking portable setup options...")
         portable_gcc = download_compiler()
         
         if portable_gcc and os.path.exists(portable_gcc):
             print(f"[*] Using portable GCC at {portable_gcc}")
             os.environ["PATH"] += os.pathsep + os.path.dirname(portable_gcc)
             has_gcc = True
         else:
             print("\n[CRITICAL ERROR] No C compiler found and portable setup failed!")
             return False

    # Try using the batch script instructions manually (or via script) but we prefer script logic now
    # Since batch script might fail if path implies spaces or weirdness, let's just run the command directly here if GCC found
    
    # helper to run compile
    def try_compile_cmd(cwd):
        cmd = [
            "gcc", "-o", "assess.exe",
            "src/assess.c", "src/frequency.c", "src/blockFrequency.c", "src/cusum.c", 
            "src/runs.c", "src/longestRunOfOnes.c", "src/serial.c", "src/rank.c", 
            "src/discreteFourierTransform.c", "src/nonOverlappingTemplateMatchings.c", 
            "src/overlappingTemplateMatchings.c", "src/universal.c", "src/approximateEntropy.c", 
            "src/randomExcursions.c", "src/randomExcursionsVariant.c", "src/linearComplexity.c", 
            "src/dfft.c", "src/cephes.c", "src/matrix.c", "src/utilities.c", 
            "src/generators.c", "src/genutils.c", 
            "-I", "include", "-lm"
        ]
        print("[*] Running compilation command...")
        subprocess.run(cmd, cwd=cwd, check=True)

    if has_gcc:
        try:
            try_compile_cmd(nist_dir)
            if os.path.exists(assess_exe):
                return True
        except subprocess.CalledProcessError as e:
            print(f"[!] System compiler failed: {e}")
            print("[*] This often happens if MinGW is missing components (like cc1.exe).")
            # Fallthrough to portable download
            
    # If we are here, either no GCC found OR system GCC failed.
    # We must try portable setup.
    print("\n[!] Compiler issue detected. Attempting to download portable MinGW...")
    portable_gcc = download_compiler()
         
    if portable_gcc and os.path.exists(portable_gcc):
         print(f"[*] Using portable GCC at {portable_gcc}")
         # Prepend to PATH to ensure we use this one
         os.environ["PATH"] = os.path.dirname(portable_gcc) + os.pathsep + os.environ["PATH"]
         try:
             try_compile_cmd(nist_dir)
             if os.path.exists(assess_exe):
                 return True
         except subprocess.CalledProcessError as e:
             print(f"[!] Portable compilation failed: {e}")
             return False
    else:
         print("\n[CRITICAL ERROR] Portable setup failed and no working system compiler found!")
         return False
            
    return os.path.exists(assess_exe)

def run_ngrok():
    """Starts ngrok in a separate thread."""
    print("[*] Starting ngrok tunnel for port 5000...")
    try:
        # Using subprocess to run ngrok command directly
        process = subprocess.Popen(['ngrok', 'http', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[*] ngrok should be running. Check http://localhost:4040 for status.")
        process.wait()
    except FileNotFoundError:
        print("[!] ngrok not found in PATH. Please install ngrok and ensure it's in your PATH.")
    except Exception as e:
        print(f"[!] Error running ngrok: {e}")

def run_flask():
    """Starts the Flask application."""
    print("[*] Starting Flask application...")
    app_path = os.path.join(os.path.dirname(__file__), 'nist_gui', 'app.py')
    subprocess.run([sys.executable, app_path], check=True)

def main():
    print("--- NIST STS Setup & Runner ---")
    
    # 1. Compile Check
    if not compile_assess():
        print("\nWithout 'assess.exe', the application cannot function.")
        input("Press Enter to exit...")
        return

    # 2. Start ngrok in background
    ngrok_thread = threading.Thread(target=run_ngrok, daemon=True)
    ngrok_thread.start()
    
    # Give ngrok a moment to start
    time.sleep(2)

    # 3. Start Flask App
    try:
        run_flask()
    except KeyboardInterrupt:
        print("\n[*] Stopping...")

if __name__ == "__main__":
    main()
