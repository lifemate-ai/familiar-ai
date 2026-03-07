@echo off
setlocal

cd /d "%~dp0"

rem build.bat              -- PyInstaller only (dist\familiar-ai\)
rem build.bat --installer  -- PyInstaller + Inno Setup (dist\familiar-ai-setup.exe)
rem build.bat --help       -- show all options

if "%~1"=="--installer" (
  shift
  uv run --with pyinstaller python scripts/build_release.py %*
) else if "%~1"=="" (
  uv run --with pyinstaller python scripts/build_windows.py --mode onedir --name familiar-ai
) else (
  uv run --with pyinstaller python scripts/build_windows.py %*
)

if errorlevel 1 exit /b %errorlevel%
exit /b 0
