@echo off
setlocal
cd /d "%~dp0"
call SETUP_WINDOWS.bat
if errorlevel 1 exit /b 1
call RUN_TESTS.bat
if errorlevel 1 exit /b 1
call CHECK_RELEASE.bat
exit /b %errorlevel%
