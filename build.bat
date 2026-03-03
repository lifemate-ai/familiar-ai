@echo off
setlocal

cd /d "%~dp0"

if "%~1"=="" (
  uv run python scripts/release_testflight_windows.py --mode onefile --name familiar-testflight
) else (
  uv run python scripts/release_testflight_windows.py %*
)

if errorlevel 1 exit /b %errorlevel%
exit /b 0
