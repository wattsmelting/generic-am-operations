@echo off
setlocal
cd /d "%~dp0"
title Generic AM Operations v0.4.0
call SETUP_WINDOWS.bat
if errorlevel 1 goto failed
call RUN_TESTS.bat
if errorlevel 1 goto failed
call CHECK_RELEASE.bat
if errorlevel 1 goto failed
echo Opening local GUI at http://127.0.0.1:8000/
start "" "http://127.0.0.1:8000/"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto failed
exit /b 0
:failed
echo Startup failed. Review the messages above.
pause
exit /b 1
