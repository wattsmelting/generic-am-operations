@echo off
setlocal
cd /d "%~dp0"
echo [1/2] Preparing Python environment...
if exist ".venv\Scripts\python.exe" goto install
where py >nul 2>nul
if not errorlevel 1 (
  py -3 -m venv .venv
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERROR: Python 3 was not found. Install Python 3.10+ and try again.
    exit /b 1
  )
  python -m venv .venv
)
if errorlevel 1 (
  echo ERROR: Could not create the virtual environment.
  exit /b 1
)
:install
echo [2/2] Installing required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo ERROR: Dependency installation failed.
  exit /b 1
)
echo Setup complete.
exit /b 0
