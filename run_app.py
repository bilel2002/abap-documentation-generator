"""
run_app.py — PyInstaller-compatible Streamlit launcher.

KEY FIX: Uses stcli.main() to run Streamlit IN-PROCESS instead of subprocess.
         In a frozen .exe, sys.executable points back to the .exe itself, so
         subprocess.run([sys.executable, "-m", "streamlit", ...]) re-launches
         the .exe infinitely, opening a new browser tab each time.
"""

import multiprocessing
import sys
import os
import time
import threading
import webbrowser
import requests

# ── CRITICAL: must be the very first thing for PyInstaller + multiprocessing ──
# Without this, any package that uses multiprocessing internally (e.g. torch,
# sentence-transformers) will spawn infinite child processes when frozen.
multiprocessing.freeze_support()


# ── Config ────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434"
OLLAMA_MODEL = "mistral:7b-instruct"
APP_PORT     = 8503


def resource_path(relative_path: str) -> str:
    """Return absolute path — works in dev and in PyInstaller .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path)


# ── Ollama health check ───────────────────────────────────────────────────────

def check_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def check_model_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if r.status_code == 200:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            return any(OLLAMA_MODEL.split(":")[0] in m for m in models)
    except Exception:
        pass
    return False


def ollama_health_check() -> bool:
    print("=" * 56)
    print("  ABAP Documentation Generator")
    print("=" * 56)
    print()
    print(f"[CHECK] Verifying Ollama is running at {OLLAMA_URL}...")

    if not check_ollama_running():
        print()
        print("  [ERROR] OLLAMA IS NOT RUNNING")
        print()
        print("  Please start Ollama before launching this app:")
        print("    1. Open a terminal")
        print("    2. Run:  ollama serve")
        print("       (or Ollama starts automatically if you installed the desktop app)")
        print()
        print("  Download Ollama at: https://ollama.com/download")
        print()
        input("  Press Enter to exit...")
        return False

    print(f"  [OK] Ollama is running")
    print(f"[CHECK] Verifying model '{OLLAMA_MODEL}' is available...")

    if not check_model_available():
        print()
        print(f"  [ERROR] MODEL NOT FOUND: {OLLAMA_MODEL}")
        print()
        print("  Please pull the model first:")
        print(f"    ollama pull {OLLAMA_MODEL}")
        print()
        input("  Press Enter to exit...")
        return False

    print(f"  [OK] Model '{OLLAMA_MODEL}' is ready")
    print()
    return True


# ── Browser opener ────────────────────────────────────────────────────────────

def open_browser(port: int = APP_PORT, delay: float = 4.0):
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":

    # 1. Ollama health check
    if not ollama_health_check():
        sys.exit(1)

    # 2. Open browser in background
    threading.Thread(target=open_browser, args=(APP_PORT,), daemon=True).start()

    print(f"[START] Launching app on http://localhost:{APP_PORT}")
    print("        Press Ctrl+C to stop.")
    print()

    # 3. Run Streamlit IN-PROCESS
    app_path = resource_path("app.py")

    # Disable development mode — required in frozen .exe because Streamlit
    # detects an editable install and sets developmentMode=True, which
    # conflicts with server.port being explicitly set.
    os.environ["STREAMLIT_DEVELOPMENT_MODE"] = "false"

    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit", "run", app_path,
        "--server.port",              str(APP_PORT),
        "--server.headless",          "true",
        "--server.runOnSave",         "false",
        "--global.developmentMode",   "false",
        "--browser.gatherUsageStats", "false",
    ]
    stcli.main()
