============================================================
  ABAP Documentation Generator
  Setup & Usage Instructions
============================================================

REQUIREMENTS
------------
This app uses a local AI model (Ollama) to generate
ABAP documentation. You need to install Ollama once
before running the app.


STEP 1 — Install Ollama
-----------------------
Download and install Ollama from:
  https://ollama.com/download

Run the installer and follow the on-screen instructions.
Ollama will run as a background service automatically
after installation.


STEP 2 — Download the AI Model (One-time, ~4 GB)
-------------------------------------------------
Open a terminal (Command Prompt or PowerShell) and run:

  ollama pull mistral:7b-instruct

Wait for the download to complete. This is a one-time step.
You do NOT need to repeat this on future launches.


STEP 3 — Build the App (First time only)
-----------------------------------------
If you cloned this project from GitHub and do not yet have
the ABAPDocGenerator.exe, you need to build it first:

  1. Make sure Python and the .venv are set up:
       python -m venv .venv
       .venv\Scripts\activate
       pip install -r requirements.txt

  2. Double-click build.bat  (or run it in a terminal)

  The build script will:
    - Install PyInstaller and Pillow automatically
    - Convert the logo to an icon
    - Bundle everything into dist\ABAPDocGenerator\
    - Copy all required data files

  This takes 5-15 minutes depending on your machine.
  You only need to do this ONCE (or after code changes).


STEP 4 — Launch the App
------------------------
Double-click:  dist\ABAPDocGenerator\ABAPDocGenerator.exe

The app will:
  1. Check that Ollama is running
  2. Check that the AI model is available
  3. Start the local web server
  4. Open your browser automatically at http://localhost:8503

If the browser does not open automatically, navigate to:
  http://localhost:8503


TROUBLESHOOTING
---------------

Problem: "OLLAMA IS NOT RUNNING"
  Solution: Make sure Ollama is installed and running.
  Open a terminal and run: ollama serve
  Or restart the Ollama desktop application.

Problem: "MODEL NOT FOUND: mistral:7b-instruct"
  Solution: Open a terminal and run:
  ollama pull mistral:7b-instruct

Problem: App opens but AI generates nothing / errors
  Solution: Make sure Ollama is not overloaded.
  Try restarting Ollama: open a terminal and run:
  ollama serve

Problem: Port 8503 already in use
  Solution: Close any other running instance of the app,
  or restart your computer.

Problem: build.bat fails
  Solution: Make sure the .venv exists and is activated.
  Run: python -m venv .venv && .venv\Scripts\activate
  Then run build.bat again.


SYSTEM REQUIREMENTS
-------------------
  - Windows 10 or Windows 11 (64-bit)
  - At least 8 GB RAM (16 GB recommended for mistral:7b-instruct)
  - At least 10 GB free disk space (for Ollama + model + build)
  - Python 3.10+ (only needed for the build step)
  - Ollama installed: https://ollama.com/download


NOTES
-----
  - The app runs entirely locally. No internet connection
    is required after setup (except for the initial model
    download).
  - Your ABAP files are never sent to any external server.
  - The chroma_db folder stores your document embeddings.
    Do not delete it unless you want to reset the knowledge
    base.
  - The dist\ folder is NOT included in the GitHub repo
    (too large). Always build locally using build.bat.

============================================================
