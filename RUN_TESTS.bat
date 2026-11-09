@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Run SETUP_WINDOWS.bat first.
  exit /b 1
)
".venv\Scripts\python.exe" -m pytest -q
exit /b %errorlevel%
