@echo off
setlocal EnableExtensions

for %%I in ("%~dp0\..\..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"

REM ==============================================================================
REM  SCRIPT DE CONFIGURACION DE ENTORNO (SETUP)
REM  -----------------------------------------------------------------------------
REM  PROPOSITO: Crear el entorno virtual e instalar dependencias.
REM
REM  SOLUCION DE PROBLEMAS COMUNES:
REM  1. Si dice "Python no encontrado": Instala Python 3.11 desde python.org
REM     y marca la casilla "Add to PATH".
REM  2. Si falla instalando librerias: Verifica tu conexion a internet.
REM     Este script ya incluye un timeout extendido (100s) para conexiones lentas.
REM ==============================================================================

set "VENV_DIR=.venv"
set "REQ=requirements.txt"
set "PY_CMD="
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PIPLOG=%TEMP%\setup_amp_pip.log"

echo [0/5] Buscando Python compatible (3.11 o 3.12)...
REM Nuitka + MinGW64 aun no soportan bien Python 3.13 ni 3.14.
REM Por eso forzamos la busqueda de versiones estables.

REM --- PRIORIDAD: Buscar Python 3.11 o 3.12 para Nuitka ---
call :trypy py -3.11
if defined PY_CMD goto py_ok

call :trypy py -3.12
if defined PY_CMD goto py_ok

REM --- FALLBACK: Intentar lo que haya (pero avisar si es muy nuevo) ---
call :trypy py -3
if not defined PY_CMD call :trypy python

if defined PY_CMD goto py_ok
echo.
echo ERROR: No se encontro una version de Python compatible.
echo Por favor instala Python 3.11 desde python.org
echo.
exit /b 1

:py_ok
echo Usando Python: %PY_CMD%

echo [1/5] Creating virtual environment in `%VENV_DIR%`...
REM Borramos el entorno anterior si existe para evitar mezclar versiones
if exist "%VENV_DIR%" (
    echo El entorno virtual ya existe. Eliminando para crear uno limpio con la nueva version...
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
exit /b 1
)
REM Aumentamos el timeout a 100 segundos para evitar errores de red con Nuitka
"%VENV_PY%" -m pip install -r "%REQ%" --default-timeout=100
if errorlevel 1 goto install_fail

echo [4/5] Setup complete.
echo.
echo [5/5] Entorno listo.
echo.
endlocal
exit /b 0

:trypy
set "candidate=%*"
%candidate% --version >nul 2>&1
if not errorlevel 1 if not defined PY_CMD set "PY_CMD=%candidate%"
goto :eof

:venv_fail
echo ERROR: Failed to create the virtual environment.
exit /b 1

:install_fail
echo ERROR: Failed to install requirements from `%REQ%`.
echo This is likely due to a Python version incompatibility with your packages.
echo Your current Python is:
"%VENV_PY%" --version
exit /b 1
