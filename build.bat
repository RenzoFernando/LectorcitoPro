@echo off
setlocal

REM --- Definicion de variables para la compilacion ---
set "APP_NAME=LectorcitoPro"
set "ENTRY_POINT=src/main.py"
set "ICON_FILE=recursos/lector.ico"
set "RESOURCES_FOLDER=recursos"
set "OUTPUT_FOLDER=descargas"

echo.
echo =======================================================
echo  Compilador para %APP_NAME%
echo =======================================================
echo.

REM --- Verificacion e instalacion de dependencias ---
echo Verificando PyInstaller...
pip show pyinstaller > nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller no encontrado. Intentando instalar...
    pip install pyinstaller
    echo.
    echo Verificando de nuevo la instalacion de PyInstaller...
    pip show pyinstaller > nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo ERROR: La instalacion de PyInstaller fallo.
        echo Por favor, ejecute "pip install pyinstaller" manualmente y vuelva a intentarlo.
        goto :eof
    )
    echo PyInstaller instalado correctamente.
) else (
    echo PyInstaller ya esta instalado.
)
echo.

echo Verificando dependencias de requirements.txt...
pip install -r requirements.txt
echo Dependencias de requirements.txt estan al dia.
echo.


REM --- Limpieza de directorios de compilaciones anteriores ---
echo Limpiando artefactos de compilaciones anteriores...
if exist "build" (
    echo  - Borrando carpeta 'build\'
    rmdir /s /q build
)
if exist "dist" (
    echo  - Borrando carpeta 'dist\'
    rmdir /s /q dist
)
if exist "%APP_NAME%.spec" (
    echo  - Borrando '%APP_NAME%.spec'
    del "%APP_NAME%.spec"
)
echo Limpieza completada.
echo.


REM --- Compilacion de la aplicacion con PyInstaller ---
echo =======================================================
echo  Iniciando compilacion con PyInstaller...
echo =======================================================
echo.

REM --onefile: Empaqueta todo en un solo archivo ejecutable.
REM --noconsole: Ejecuta la aplicacion GUI sin una ventana de terminal.
REM --name: Especifica el nombre del archivo .exe de salida.
REM --icon: Asigna el icono al ejecutable.
REM --add-data: Incluye la carpeta de recursos dentro del .exe.
REM --paths: Agrega la carpeta 'src' para resolver importaciones locales.
pyinstaller --onefile --noconsole --name "%APP_NAME%" --icon="%ICON_FILE%" --add-data="%RESOURCES_FOLDER%;%RESOURCES_FOLDER%" --paths src "%ENTRY_POINT%"

REM --- Verificacion del resultado de la compilacion ---
if %errorlevel% neq 0 (
    echo.
    echo ******************************************************
    echo * ERROR: La compilacion con PyInstaller fallo.      *
    echo ******************************************************
    goto :eof
)

echo.
echo =======================================================
echo  Compilacion exitosa!
echo =======================================================
echo.

REM --- Organizacion del archivo ejecutable ---
echo Moviendo %APP_NAME%.exe a la carpeta '%OUTPUT_FOLDER%'...
if not exist "%OUTPUT_FOLDER%" (
    mkdir "%OUTPUT_FOLDER%"
)

move "dist\%APP_NAME%.exe" "%OUTPUT_FOLDER%\"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo mover el archivo. Busquelo en la carpeta 'dist\'.
) else (
    echo El archivo %APP_NAME%.exe esta listo en la carpeta '%OUTPUT_FOLDER%'.
)
echo.

REM --- Limpieza final de archivos temporales ---
echo Limpiando archivos temporales restantes...
rmdir /s /q build
del "%APP_NAME%.spec"
rmdir /s /q dist
echo.

echo =======================================================
echo  PROCESO COMPLETADO
echo =======================================================
echo.

pause
endlocal

:: .\build.bat