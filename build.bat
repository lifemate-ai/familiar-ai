@echo off
setlocal

cd /d "%~dp0"

if "%~1"=="" (
  uv run --with pyinstaller python scripts/build_windows.py --mode onedir --name familiar-ai
) else (
  uv run --with pyinstaller python scripts/build_windows.py %*
)

if errorlevel 1 exit /b %errorlevel%
exit /b 0
