@echo off
setlocal EnableExtensions
chcp 65001 >nul
REM ==============================================================================
REM  COMPILADOR NUITKA (ANTIVIRUS FRIENDLY)
REM  -----------------------------------------------------------------------------
REM  PROPOSITO: Convertir el codigo Python a C++ y luego a .exe
REM
REM  >>> SOLUCION DE PROBLEMAS DE DESCARGA (PLAN B) <<<
REM  Si Nuitka falla descargando "MinGW64" o "Dependency Walker" por internet lento:
REM
REM  1. DESCARGA MANUAL GCC (Compilador C):
REM     - URL: https://github.com/brechtsanders/winlibs_mingw/releases/download/14.2.0posix-19.1.1-12.0.0-msvcrt-r2/winlibs-x86_64-posix-seh-gcc-14.2.0-llvm-19.1.1-mingw-w64msvcrt-12.0.0-r2.zip
REM     - RUTA: %LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\gcc\x86_64\14.2.0posix-19.1.1-12.0.0-msvcrt-r2\
REM     - ACCION: Pegar el ZIP descargado en esa carpeta (sin descomprimir).
REM
REM  2. DESCARGA MANUAL DEPENDENCY WALKER:
REM     - URL: http://dependencywalker.com/depends22_x64.zip
REM     - RUTA: %LOCALAPPDATA%\Nuitka\Nuitka\Cache\downloads\depends\x86_64\
REM     - ACCION: Descomprimir el ZIP ahi. Debe quedar "depends.exe" visible.
REM ==============================================================================

for %%I in ("%~dp0\..\..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"
set "ENTRY_POINT=src/main.py"
set "VENV_PYTHON=.venv-build\Scripts\python.exe"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

echo.
echo =======================================================
echo  Compilador de Aplicacion Portable (Motor: Nuitka)
echo =======================================================

echo.

REM --- Seleccion Forzada de Python ---
REM Esto evita que la terminal use Python 3.14 por error si esta instalado en el sistema
if exist "%VENV_PYTHON%" (
    echo [INFO] Entorno virtual detectado. Usando Python 3.11 desde .venv-build
    set "PYTHON_CMD=%VENV_PYTHON%"
) else (
    echo [WARN] No se detecto .venv-build. Usando Python del sistema - riesgo de error.
    set "PYTHON_CMD=python"
)

REM --- Verificacion de version ---
echo Version detectada:
"%PYTHON_CMD%" --version

echo.

"%PYTHON_CMD%" "src\app_meta.py"
if errorlevel 1 goto :meta_error
call :read_meta APP_NAME app_meta.APP_NAME_INTERNAL
if errorlevel 1 goto :meta_error
call :read_meta APP_EXE_NAME app_meta.APP_EXECUTABLE_NAME
if errorlevel 1 goto :meta_error
call :read_meta ICON_FILE app_meta.APP_ICON_ICO_RELATIVE_PATH
if errorlevel 1 goto :meta_error
call :read_meta RESOURCES_FOLDER app_meta.APP_RESOURCES_DIR_NAME
if errorlevel 1 goto :meta_error
call :read_meta OUTPUT_FOLDER app_meta.APP_OUTPUT_DIR_NAME
if errorlevel 1 goto :meta_error
call :read_meta PRODUCT_NAME app_meta.APP_PRODUCT_NAME
if errorlevel 1 goto :meta_error
call :read_meta FILE_DESCRIPTION app_meta.APP_FILE_DESCRIPTION
if errorlevel 1 goto :meta_error
call :read_meta PRODUCT_VERSION app_meta.APP_PRODUCT_VERSION
if errorlevel 1 goto :meta_error
call :read_meta FILE_VERSION app_meta.APP_FILE_VERSION
if errorlevel 1 goto :meta_error
call :read_meta COMPANY_NAME app_meta.APP_COMPANY_NAME
if errorlevel 1 goto :meta_error
call :read_meta COPYRIGHT_TEXT app_meta.APP_LEGAL_COPYRIGHT
if errorlevel 1 goto :meta_error
call :read_meta TRADEMARK_TEXT app_meta.APP_TRADEMARK
if errorlevel 1 goto :meta_error
call :read_meta PORTABLE_ARTIFACT_NAME app_meta.APP_PORTABLE_ARTIFACT_NAME
if errorlevel 1 goto :meta_error
call :read_meta LICENSE_FILE app_meta.APP_LICENSE_RELATIVE_PATH
if errorlevel 1 goto :meta_error

if not exist "%LICENSE_FILE%" (
    echo.
    echo ******************************************************
    echo * ERROR: No se encontro el archivo de licencia.      *
    echo * Falta: %LICENSE_FILE%                              *
    echo ******************************************************
    endlocal
    exit /b 1
)

echo Metadatos detectados:
echo [APP] %APP_NAME%
echo [EXE] %APP_EXE_NAME%
echo [ICON] %ICON_FILE%
echo [RESOURCES] %RESOURCES_FOLDER%
echo [OUTPUT] %OUTPUT_FOLDER%
echo [PRODUCT] %PRODUCT_NAME%
echo [DESCRIPTION] %FILE_DESCRIPTION%
echo [PRODUCT VERSION] %PRODUCT_VERSION%
echo [FILE VERSION] %FILE_VERSION%
echo [COMPANY] %COMPANY_NAME%
echo [COPYRIGHT] %COPYRIGHT_TEXT%
echo [TRADEMARK] %TRADEMARK_TEXT%
echo [PORTABLE] %PORTABLE_ARTIFACT_NAME%
echo [LICENSE] %LICENSE_FILE%

echo.

echo Verificando Nuitka y dependencias...
"%PYTHON_CMD%" -m pip check > nul
if errorlevel 1 goto :dependency_error
"%PYTHON_CMD%" -c "import appdirs, customtkinter, PIL, nuitka; import win32com.client" > nul 2>&1
if errorlevel 1 goto :dependency_error

echo.

REM --- Limpieza de compilaciones anteriores ---
echo Limpiando artefactos anteriores...
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.dist" rmdir /s /q "%APP_NAME%.dist"
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
if exist "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" del /q "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" > nul 2>&1
if exist "%OUTPUT_FOLDER%\%LICENSE_FILE%" del /q "%OUTPUT_FOLDER%\%LICENSE_FILE%" > nul 2>&1
echo Limpieza completada.

echo.

REM --- Compilacion con Nuitka ---
echo =======================================================
echo  Iniciando compilacion de codigo a C++...
echo  NOTA: Si te pregunta "Proceed and download?", escribe: Yes
echo =======================================================

echo.
REM Flags explicados:
REM --windows-console-mode=disable : Oculta la consola negra (estilo moderno)
REM --standalone --onefile : Crea un solo archivo .exe portatil
REM --enable-plugin=tk-inter : Necesario para interfaces graficas

"%PYTHON_CMD%" -m nuitka --mode=onefile ^
    --assume-yes-for-downloads ^
    --output-filename="%APP_EXE_NAME%" ^
    --windows-icon-from-ico="%ICON_FILE%" ^
    --windows-console-mode=disable ^
    --company-name="%COMPANY_NAME%" ^
    --product-name="%PRODUCT_NAME%" ^
    --file-description="%FILE_DESCRIPTION%" ^
    --file-version="%FILE_VERSION%" ^
    --product-version="%PRODUCT_VERSION%" ^
    --copyright="%COPYRIGHT_TEXT%" ^
    --trademark="%TRADEMARK_TEXT%" ^
    --enable-plugin=tk-inter ^
    --include-package=customtkinter ^
    --include-data-dir="%RESOURCES_FOLDER%=%RESOURCES_FOLDER%" ^
    --output-dir=dist ^
    --remove-output ^
    "%ENTRY_POINT%"
if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo * ERROR: La compilacion fallo.                       *
    echo * REVISA LA SECCION DE "PLAN B" AL INICIO DE ESTE    *
    echo * ARCHIVO SI EL ERROR FUE DE DESCARGA.               *
    echo ******************************************************
    endlocal
    exit /b 1
)

echo.
echo =======================================================
echo  Compilacion portable exitosa!
echo =======================================================

echo.

REM --- Organizacion del archivo ejecutable ---
echo Moviendo artefacto portable a la carpeta '%OUTPUT_FOLDER%'...
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"
move "dist\%APP_EXE_NAME%" "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" > nul
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo mover el archivo. Busquelo en la carpeta 'dist\'.
    if exist "dist" rmdir /s /q dist
    if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
    if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
    endlocal
    exit /b 1
) else (
    echo El archivo %PORTABLE_ARTIFACT_NAME% esta listo en la carpeta '%OUTPUT_FOLDER%'.
)

echo.

REM --- Limpieza final ---
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
endlocal
exit /b 0

:read_meta
set "%~1="
set "META_VALUE_FILE=%TEMP%\LectorcitoPro_meta_%RANDOM%_%RANDOM%.tmp"
"%PYTHON_CMD%" -c "import os,sys; sys.path.insert(0, os.path.abspath('src')); import app_meta; print(%~2)" > "%META_VALUE_FILE%"
if errorlevel 1 (
    if exist "%META_VALUE_FILE%" del /q "%META_VALUE_FILE%" > nul 2>&1
    exit /b 1
)
set /p "%~1="<"%META_VALUE_FILE%"
del /q "%META_VALUE_FILE%" > nul 2>&1
if not defined %~1 exit /b 1
exit /b 0

:dependency_error

echo.
echo ******************************************************
echo * ERROR: Faltan dependencias del entorno.             *
echo * Ejecuta primero scripts\windows\setup.bat.          *
echo ******************************************************
exit /b 1

:meta_error

echo.
echo ******************************************************
echo * ERROR: No se pudieron cargar los metadatos desde   *
echo * 'src\app_meta.py'.                                 *
echo ******************************************************
exit /b 1
