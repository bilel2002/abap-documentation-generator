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


STEP 2 — Download the AI Model (One-time, ~5 GB)
-------------------------------------------------
Open a terminal (Command Prompt or PowerShell) and run:

  ollama pull llama3.1:latest

Wait for the download to complete. This is a one-time step.
You do NOT need to repeat this on future launches.


STEP 3 — Launch the App
------------------------
Double-click:  ABAPDocGenerator.exe

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

Problem: "MODEL NOT FOUND: llama3.1:latest"
  Solution: Open a terminal and run:
  ollama pull mistral:7b-instruct

Problem: App opens but AI generates nothing / errors
  Solution: Make sure Ollama is not overloaded.
  Try restarting Ollama: open a terminal and run:
  ollama serve

Problem: Port 8503 already in use
  Solution: Close any other running instance of the app,
  or restart your computer.


SYSTEM REQUIREMENTS
-------------------
  - Windows 10 or Windows 11 (64-bit)
  - At least 8 GB RAM (16 GB recommended for mistral:7b-instruct)
  - At least 10 GB free disk space (for Ollama + model)
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

============================================================
