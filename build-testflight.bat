@echo off
setlocal

cd /d "%~dp0"

if "%~1"=="" (
  call build.bat
) else (
  call build.bat %*
)

exit /b %errorlevel%
