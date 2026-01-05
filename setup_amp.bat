@echo off
setlocal EnableExtensions

set "VENV_DIR=.venv"
set "REQ=requirements.txt"
set "PY_CMD="
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PIPLOG=%TEMP%\setup_amp_pip.log"

echo [0/5] Searching for Python...
call :trypy py -3
call :trypy python3
call :trypy python

if defined PY_CMD goto py_ok
echo ERROR: No Python executable found. Please install Python and ensure it's in your PATH.
pause
exit /b 1

:py_ok
echo Using: %PY_CMD%

echo [1/5] Creating virtual environment in `%VENV_DIR%`...
if exist "%VENV_PY%" (
    echo Virtual environment already exists. Re-creating for a clean install.
    rmdir /S /Q "%VENV_DIR%"
)
%PY_CMD% -m venv "%VENV_DIR%"
if errorlevel 1 goto venv_fail

:venv_py_ok
echo [2/5] Upgrading core tooling (pip/setuptools/wheel)...
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel > "%PIPLOG%" 2>&1
if errorlevel 1 echo WARNING: pip tooling upgrade failed. See `%PIPLOG%`.

echo [3/5] Installing requirements from `%REQ%`...
if not exist "%REQ%" (
    echo ERROR: `%REQ%` not found. Cannot install dependencies.
    pause
    exit /b 1
)
"%VENV_PY%" -m pip install -r "%REQ%"
if errorlevel 1 goto install_fail

echo [4/5] Setup complete.
echo.
echo [5/5] To activate the virtual environment, run one of the following commands:
echo.
echo   In PowerShell:
echo   .\%VENV_DIR%\Scripts\Activate.ps1
echo.
echo   In Command Prompt (CMD):
echo   %VENV_DIR%\Scripts\activate.bat
echo.
pause
exit /b 0

:trypy
set "candidate=%*"
%candidate% --version >nul 2>&1
if not errorlevel 1 if not defined PY_CMD set "PY_CMD=%candidate%"
goto :eof

:venv_fail
echo ERROR: Failed to create the virtual environment.
pause
exit /b 1

:install_fail
echo ERROR: Failed to install requirements from `%REQ%`.
echo This is likely due to a Python version incompatibility with your packages.
echo Your current Python is:
"%VENV_PY%" --version
echo Please check the package requirements, especially for `pyinstaller`.
pause
exit /b 1

:: .\setup_amp.bat