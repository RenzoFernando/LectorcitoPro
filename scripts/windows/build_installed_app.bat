@echo off
setlocal EnableExtensions
chcp 65001 >nul
for %%I in ("%~dp0\..\..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"

set "ENTRY_POINT=src/main.py"
set "VENV_PYTHON=.venv-build\Scripts\python.exe"
set "INSTALLED_BUILD_ROOT=build\windows\installed-app"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if not exist "%VENV_PYTHON%" (
    echo ERROR: No existe el entorno .venv-build. Ejecuta primero scripts\windows\setup.bat.
    exit /b 1
)
set "PYTHON_CMD=%VENV_PYTHON%"

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

set "INSTALLED_DIST_DIR=%INSTALLED_BUILD_ROOT%\%APP_NAME%.dist"

"%PYTHON_CMD%" -m pip check > nul
if errorlevel 1 goto :dependency_error
"%PYTHON_CMD%" -c "import appdirs, customtkinter, PIL, nuitka; import win32com.client" > nul 2>&1
if errorlevel 1 goto :dependency_error

if exist "%INSTALLED_BUILD_ROOT%" rmdir /s /q "%INSTALLED_BUILD_ROOT%"
if not exist "build\windows" mkdir "build\windows"
mkdir "%INSTALLED_BUILD_ROOT%"

"%PYTHON_CMD%" -m nuitka --mode=standalone ^
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
    --output-dir="%INSTALLED_BUILD_ROOT%" ^
    --remove-output ^
    "%ENTRY_POINT%"
if errorlevel 1 exit /b 1

if not exist "%INSTALLED_DIST_DIR%" (
    for /d %%D in ("%INSTALLED_BUILD_ROOT%\*.dist") do (
        if not exist "%INSTALLED_DIST_DIR%" move "%%~fD" "%INSTALLED_DIST_DIR%" > nul
    )
)

if not exist "%INSTALLED_DIST_DIR%\%APP_EXE_NAME%" (
    echo ERROR: No se genero la distribucion standalone esperada.
    exit /b 1
)

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
echo ERROR: Faltan dependencias del entorno. Ejecuta primero scripts\windows\setup.bat.
exit /b 1

:meta_error
echo ERROR: No se pudieron cargar los metadatos desde src\app_meta.py.
exit /b 1
