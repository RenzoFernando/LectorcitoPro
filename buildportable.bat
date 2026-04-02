@echo off
setlocal

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

cd /d "%~dp0"

set "ENTRY_POINT=src/main.py"
set "VENV_PYTHON=.venv\Scripts\python.exe"
set "META_EXPORT_SCRIPT=.build_meta_export.py"
set "META_EXPORT_CMD=.build_meta_export.cmd"
set "PORTABLE_ARTIFACT_NAME=Lectorcito Pro Portable.exe"

echo.
echo =======================================================
echo  Compilador de Aplicacion Portable (Motor: Nuitka)
echo =======================================================
echo.

REM --- Seleccion Forzada de Python ---
REM Esto evita que la terminal use Python 3.14 por error si esta instalado en el sistema
if exist "%VENV_PYTHON%" (
    echo [INFO] Entorno virtual detectado. Usando Python 3.11 desde .venv
    set "PYTHON_CMD=%VENV_PYTHON%"
) else (
    echo [WARN] No se detecto .venv. Usando Python del sistema - riesgo de error.
    set "PYTHON_CMD=python"
)

REM --- Verificacion de version ---
echo Version detectada:
"%PYTHON_CMD%" --version
echo.

if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1

> "%META_EXPORT_SCRIPT%" echo import os
>> "%META_EXPORT_SCRIPT%" echo import sys
>> "%META_EXPORT_SCRIPT%" echo sys.path.insert^(0, os.path.abspath^("src"^)^)
>> "%META_EXPORT_SCRIPT%" echo import app_meta
>> "%META_EXPORT_SCRIPT%" echo meta = [
>> "%META_EXPORT_SCRIPT%" echo     ("APP_NAME", app_meta.APP_NAME_INTERNAL),
>> "%META_EXPORT_SCRIPT%" echo     ("APP_EXE_NAME", app_meta.APP_EXECUTABLE_NAME),
>> "%META_EXPORT_SCRIPT%" echo     ("ICON_FILE", app_meta.APP_ICON_ICO_RELATIVE_PATH),
>> "%META_EXPORT_SCRIPT%" echo     ("RESOURCES_FOLDER", app_meta.APP_RESOURCES_DIR_NAME),
>> "%META_EXPORT_SCRIPT%" echo     ("OUTPUT_FOLDER", app_meta.APP_OUTPUT_DIR_NAME),
>> "%META_EXPORT_SCRIPT%" echo     ("PRODUCT_NAME", app_meta.APP_PRODUCT_NAME),
>> "%META_EXPORT_SCRIPT%" echo     ("FILE_DESCRIPTION", app_meta.APP_FILE_DESCRIPTION),
>> "%META_EXPORT_SCRIPT%" echo     ("PRODUCT_VERSION", app_meta.APP_PRODUCT_VERSION),
>> "%META_EXPORT_SCRIPT%" echo     ("FILE_VERSION", app_meta.APP_FILE_VERSION),
>> "%META_EXPORT_SCRIPT%" echo     ("COMPANY_NAME", app_meta.APP_COMPANY_NAME),
>> "%META_EXPORT_SCRIPT%" echo     ("COPYRIGHT_TEXT", app_meta.APP_LEGAL_COPYRIGHT),
>> "%META_EXPORT_SCRIPT%" echo     ("TRADEMARK_TEXT", app_meta.APP_TRADEMARK),
>> "%META_EXPORT_SCRIPT%" echo ]
>> "%META_EXPORT_SCRIPT%" echo for key, value in meta:
>> "%META_EXPORT_SCRIPT%" echo     text = str^(value^).replace^('^"', ''^)
>> "%META_EXPORT_SCRIPT%" echo     print^(f'set "{key}={text}"'^)

"%PYTHON_CMD%" "%META_EXPORT_SCRIPT%" > "%META_EXPORT_CMD%"
if errorlevel 1 goto :meta_error

call "%META_EXPORT_CMD%"
if errorlevel 1 goto :meta_error

if not defined APP_NAME goto :meta_error
if not defined APP_EXE_NAME goto :meta_error
if not defined ICON_FILE goto :meta_error
if not defined RESOURCES_FOLDER goto :meta_error
if not defined OUTPUT_FOLDER goto :meta_error
if not defined PRODUCT_NAME goto :meta_error
if not defined FILE_DESCRIPTION goto :meta_error
if not defined PRODUCT_VERSION goto :meta_error
if not defined FILE_VERSION goto :meta_error
if not defined COMPANY_NAME goto :meta_error
if not defined COPYRIGHT_TEXT goto :meta_error
if not defined TRADEMARK_TEXT goto :meta_error

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
echo.

echo Instalando/Verificando Nuitka y dependencias...
"%PYTHON_CMD%" -m pip install -r requirements.txt --default-timeout=100 > nul
echo.

REM --- Limpieza de compilaciones anteriores ---
echo Limpiando artefactos anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.dist" rmdir /s /q "%APP_NAME%.dist"
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
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

"%PYTHON_CMD%" -m nuitka --onefile --standalone ^
    --output-filename="%APP_EXE_NAME%" ^
    --windows-icon-from-ico="%ICON_FILE%" ^
    --windows-console-mode=disable ^
    --windows-company-name="%COMPANY_NAME%" ^
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
    if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
    if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1
    echo.
    echo ******************************************************
    echo * ERROR: La compilacion fallo.                       *
    echo * REVISA LA SECCION DE "PLAN B" AL INICIO DE ESTE    *
    echo * ARCHIVO SI EL ERROR FUE DE DESCARGA.               *
    echo ******************************************************
    pause
    goto :eof
)

echo.
echo =======================================================
echo  Compilacion portable exitosa!
echo =======================================================
echo.

REM --- Organizacion del archivo ejecutable ---
echo Moviendo artefacto portable a la carpeta '%OUTPUT_FOLDER%'...
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"
if exist "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" del /q "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" > nul 2>&1

move "dist\%APP_EXE_NAME%" "%OUTPUT_FOLDER%\%PORTABLE_ARTIFACT_NAME%" > nul

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo mover el archivo. Busquelo en la carpeta 'dist\'.
) else (
    echo El archivo %PORTABLE_ARTIFACT_NAME% esta listo en la carpeta '%OUTPUT_FOLDER%'.
)
echo.

REM --- Limpieza final ---
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"
if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1

pause
endlocal
goto :eof

:meta_error
if exist "%META_EXPORT_SCRIPT%" del /q "%META_EXPORT_SCRIPT%" > nul 2>&1
if exist "%META_EXPORT_CMD%" del /q "%META_EXPORT_CMD%" > nul 2>&1
echo.
echo ******************************************************
echo * ERROR: No se pudieron cargar los metadatos desde   *
echo * 'src\app_meta.py'.                                 *
echo ******************************************************
pause
exit /b 1