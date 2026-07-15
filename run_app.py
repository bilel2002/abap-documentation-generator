import subprocess
import sys
import os

if __name__ == "__main__":
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    streamlit_path = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "streamlit.exe")
    subprocess.run([
        streamlit_path,
        "run", app_path,
        "--server.runOnSave", "true"
    ])
