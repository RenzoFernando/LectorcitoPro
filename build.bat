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

set "APP_NAME=LectorcitoPro"
set "ENTRY_POINT=src/main.py"
set "ICON_FILE=recursos/lector.ico"
set "RESOURCES_FOLDER=recursos"
set "OUTPUT_FOLDER=descargas"
set "VENV_PYTHON=.venv\Scripts\python.exe"

echo.
echo =======================================================
echo  Compilador para %APP_NAME% (Motor: Nuitka)
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

echo Instalando/Verificando Nuitka y dependencias...
REM Usamos el pip especifico del entorno para garantizar consistencia
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
    --output-filename="%APP_NAME%.exe" ^
    --windows-icon-from-ico="%ICON_FILE%" ^
    --windows-console-mode=disable ^
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
    pause
    goto :eof
)

echo.
echo =======================================================
echo  Compilacion exitosa!
echo =======================================================
echo.

REM --- Organizacion del archivo ejecutable ---
echo Moviendo %APP_NAME%.exe a la carpeta '%OUTPUT_FOLDER%'...
if not exist "%OUTPUT_FOLDER%" mkdir "%OUTPUT_FOLDER%"

REM Nuitka deja el exe en la carpeta definida en --output-dir (dist)
move "dist\%APP_NAME%.exe" "%OUTPUT_FOLDER%\" > nul

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo mover el archivo. Busquelo en la carpeta 'dist\'.
) else (
    echo El archivo %APP_NAME%.exe esta listo en la carpeta '%OUTPUT_FOLDER%'.
    echo Ya puede usar 'firmar_aplicacion.ps1' para firmarlo si lo desea.
)
echo.

REM --- Limpieza final ---
if exist "dist" rmdir /s /q dist
if exist "%APP_NAME%.build" rmdir /s /q "%APP_NAME%.build"
if exist "%APP_NAME%.onefile-build" rmdir /s /q "%APP_NAME%.onefile-build"

pause
endlocal