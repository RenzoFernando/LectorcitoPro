@echo off
setlocal

:: --- Configuracion ---
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

:: 1. Instalar/Verificar PyInstaller de forma robusta
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
        echo ERROR: La instalacion de PyInstaller fallo despues del intento.
        echo Por favor, ejecute "pip install pyinstaller" manualmente y vuelva a intentarlo.
        goto :eof
    )
    echo PyInstaller instalado correctamente.
) else (
    echo PyInstaller ya esta instalado.
)
echo.

:: 1.5 Instalar otras dependencias del proyecto
echo Verificando dependencias de requirements.txt...
pip install -r requirements.txt
echo Dependencias de requirements.txt estan al dia.
echo.


:: 2. Limpiar compilaciones anteriores
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


:: 3. Compilar la aplicacion con PyInstaller
echo =======================================================
echo  Iniciando compilacion con PyInstaller...
echo =======================================================
echo.

rem Este es el comando clave para empaquetar todo correctamente.
rem --onefile: Crea un unico archivo ejecutable.
rem --noconsole: Evita que se abra una ventana de consola al ejecutar la GUI.
rem --name: Define el nombre del archivo .exe final.
rem --icon: Asigna el icono al ejecutable.
rem --add-data: Anade la carpeta de recursos para que las imagenes e iconos se incluyan.
rem --paths: Anade la carpeta 'src' a la ruta de busqueda de modulos para evitar errores de importacion.
pyinstaller --onefile --noconsole --name "%APP_NAME%" --icon="%ICON_FILE%" --add-data="%RESOURCES_FOLDER%;%RESOURCES_FOLDER%" --paths src "%ENTRY_POINT%"

:: 4. Verificar si la compilacion fue exitosa
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

:: 5. Mover el ejecutable a la carpeta de descargas
echo Moviendo %APP_NAME%.exe a la carpeta '%OUTPUT_FOLDER%'...
if not exist "%OUTPUT_FOLDER%" (
    mkdir "%OUTPUT_FOLDER%"
)

rem Usamos move y verificamos el resultado
move "dist\%APP_NAME%.exe" "%OUTPUT_FOLDER%\"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo mover el archivo. Busquelo en la carpeta 'dist\'.
) else (
    echo El archivo %APP_NAME%.exe esta listo en la carpeta '%OUTPUT_FOLDER%'.
)
echo.

:: 6. Limpieza final de carpetas temporales
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
