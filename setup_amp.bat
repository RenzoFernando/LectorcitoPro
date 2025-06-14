:: setup_amp.bat
@echo off
REM ─── Paso 1: Crear el virtualenv si no existe ───────────
IF NOT EXIST ".venv\Scripts\activate.bat" (
    echo [1/5] Creando virtualenv en .venv\...
    python -m venv .venv
) ELSE (
    echo [1/5] Virtualenv ya existe.
)

REM ─── Paso 2: Activar el entorno ────────────────────────
echo [2/5] Activando virtualenv...
call .venv\Scripts\activate.bat

REM ─── Paso 3: Actualizar pip ────────────────────────────
echo [3/5] Actualizando pip...
python -m pip install --upgrade pip

REM ─── Paso 4: Instalar o actualizar dependencias ────────
IF EXIST requirements.txt (
    echo [4/5] Instalando/actualizando deps de requirements.txt...
    python -m pip install --upgrade -r requirements.txt
) ELSE (
    echo [4/5] No se encontró requirements.txt, se omitirá esta parte.
)

REM ─── Paso 5: Volver a volcar requirements.txt ──────────
echo [5/5] Regenerando requirements.txt con pip freeze...
python -m pip freeze > requirements.txt

echo.
echo ¡Setup completado! El entorno virtual está activo en esta consola.
pause

:: .\setup_amp.bat