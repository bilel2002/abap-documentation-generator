@echo off
setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo   ABAP Documentation Generator ^— Build Script
echo ============================================================
echo.

:: ── Step 0: Create virtual environment if missing ───────────────────────────
if not exist .venv (
    echo [SETUP] .venv not found — creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        echo         Make sure Python is installed and added to PATH.
        pause
        exit /b 1
    )
    echo       .venv created OK
)

:: ── Step 1: Activate virtual environment ────────────────────────────────────
echo [1/5] Activating virtual environment...
call .venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Could not activate .venv — make sure it exists.
    pause
    exit /b 1
)
echo       OK

:: ── Step 2: Install dependencies ────────────────────────────────────────────
echo [2/5] Installing dependencies from requirements.txt...
if exist requirements.txt (
    pip install -r requirements.txt --quiet
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install requirements.txt.
        pause
        exit /b 1
    )
    echo       requirements.txt installed OK
) else (
    echo       [WARN] requirements.txt not found — skipping
)

echo       Installing PyInstaller and Pillow (build tools)...
pip install pyinstaller pillow --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo       OK


:: ── Step 3: Convert logo.png -> icon.ico ────────────────────────────────────
echo [3/5] Converting logo.png to icon.ico...
python build_icon.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Icon conversion failed. Check assets\logo.png exists.
    pause
    exit /b 1
)
echo       OK

:: ── Step 4: Run PyInstaller ──────────────────────────────────────────────────
echo [4/5] Running PyInstaller (this may take several minutes)...
echo       Note: Using large-stack wrapper to avoid Windows stack overflow.
python run_pyinstaller.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller build failed. See output above.
    pause
    exit /b 1
)
echo       OK

:: ── Step 5: Copy runtime data folders ───────────────────────────────────────
echo [5/5] Copying runtime data to dist folder...

:: chroma_db (vector store — may be large)
if exist chroma_db (
    xcopy /E /I /Y /Q chroma_db dist\ABAPDocGenerator\chroma_db >nul
    echo       chroma_db copied
) else (
    echo       [SKIP] chroma_db not found ^(will be created on first run^)
)

:: data folder
if exist data (
    xcopy /E /I /Y /Q data dist\ABAPDocGenerator\data >nul
    echo       data\ copied
)

:: JSON knowledge base
if exist sap_knowledge_base.json (
    copy /Y sap_knowledge_base.json dist\ABAPDocGenerator\ >nul
    echo       sap_knowledge_base.json copied
)

:: bilelll.json (model data)
if exist bilelll.json (
    copy /Y bilelll.json dist\ABAPDocGenerator\ >nul
    echo       bilelll.json copied
)

:: model_data.json
if exist model_data.json (
    copy /Y model_data.json dist\ABAPDocGenerator\ >nul
    echo       model_data.json copied
)

:: README for end users
if exist README.txt (
    copy /Y README.txt dist\ABAPDocGenerator\ >nul
    echo       README.txt copied
)

echo.
echo ============================================================
echo   BUILD COMPLETE!
echo   Output: dist\ABAPDocGenerator\ABAPDocGenerator.exe
echo   Double-click the .exe to launch the app.
echo ============================================================
echo.
pause
