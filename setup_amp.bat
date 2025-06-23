@echo off

REM --- Paso 1: Crear el entorno virtual si no existe ---
IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [1/5] Creando entorno virtual en .venv\...
    python -m venv .venv
) ELSE (
    echo [1/5] El entorno virtual ya existe.
)

REM --- Paso 2: Activar el entorno virtual ---
echo [2/5] Activando el entorno virtual...
call .venv\Scripts\activate.bat

REM --- Paso 3: Asegurar que pip este actualizado ---
echo [3/5] Actualizando pip...
python -m pip install --upgrade pip

REM --- Paso 4: Instalar o actualizar las dependencias del proyecto ---
IF EXIST requirements.txt (
    echo [4/5] Instalando/actualizando dependencias desde requirements.txt...
    python -m pip install --upgrade -r requirements.txt
) ELSE (
    echo [4/5] Archivo requirements.txt no encontrado, se omite este paso.
)

REM --- Paso 5: Regenerar el archivo requirements.txt ---
echo [5/5] Regenerando requirements.txt para reflejar el estado actual...
python -m pip freeze > requirements.txt

echo.
echo Setup completado! El entorno virtual esta activo en esta consola.
pause

:: .\setup_amp.bat