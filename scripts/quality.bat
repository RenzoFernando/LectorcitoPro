@echo off
setlocal EnableExtensions
chcp 65001 >nul
for %%I in ("%~dp0\..") do set "PROJECT_ROOT=%%~fI"
cd /d "%PROJECT_ROOT%"

set "MODE=%~1"
if not defined MODE set "MODE=check"
if /I not "%MODE%"=="fix" if /I not "%MODE%"=="check" (
    echo ERROR: Modo invalido. Usa fix o check.
    exit /b 2
)

set "VENV_PYTHON=.venv-build\Scripts\python.exe"
set "NODE_ENV_FILE=.tools\node_env.cmd"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if not exist "%VENV_PYTHON%" (
    echo ERROR: No existe .venv-build. Ejecuta scripts\windows\setup.bat.
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "scripts\windows\setup_node.ps1" -EnvironmentFile "%NODE_ENV_FILE%"
if errorlevel 1 exit /b 1
if not exist "%NODE_ENV_FILE%" (
    echo ERROR: No se pudo preparar el entorno de Node.js.
    exit /b 1
)

call "%NODE_ENV_FILE%"
if not defined LECTORCITO_NODE_EXE exit /b 1
if not defined LECTORCITO_NPM_CMD exit /b 1

for %%I in ("%LECTORCITO_NODE_EXE%") do set "NODE_DIR=%%~dpI"
set "PATH=%NODE_DIR%;%PATH%"

call "%LECTORCITO_NPM_CMD%" install --no-package-lock --ignore-scripts --no-audit --no-fund
if errorlevel 1 exit /b 1

if /I "%MODE%"=="fix" goto :fix
goto :check

:fix
"%VENV_PYTHON%" "src\app_meta.py"
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -m ruff check src --fix
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -m ruff format src
if errorlevel 1 exit /b 1

call "node_modules\.bin\prettier.cmd" . --write --ignore-unknown
if errorlevel 1 exit /b 1

call "node_modules\.bin\eslint.cmd" "resources/js/**/*.js" --fix
if errorlevel 1 exit /b 1

exit /b 0

:check
"%VENV_PYTHON%" -m ruff check src
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -m ruff format --check src
if errorlevel 1 exit /b 1

call "node_modules\.bin\eslint.cmd" "resources/js/**/*.js"
if errorlevel 1 exit /b 1

call "node_modules\.bin\prettier.cmd" . --check --ignore-unknown
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -c "import tomllib; f=open('pyproject.toml','rb'); tomllib.load(f); f.close()"
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -m compileall -q -f src
if errorlevel 1 exit /b 1

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$failed=$false; Get-ChildItem -Path 'scripts' -Filter '*.ps1' -Recurse | ForEach-Object { $tokens=$null; $parseErrors=$null; [System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$parseErrors) | Out-Null; if ($parseErrors.Count -gt 0) { $failed=$true; $parseErrors | ForEach-Object { Write-Error ($_.Message + ' [' + $_.Extent.File + ':' + $_.Extent.StartLineNumber + ']') } } }; if ($failed) { exit 1 }"
if errorlevel 1 exit /b 1

"%VENV_PYTHON%" -c "from pathlib import Path; files=[Path('release.bat'),*Path('scripts').rglob('*.bat'),*Path('scripts').rglob('*.cmd')]; bad=[str(p) for p in files if p.is_file() and b'\n' in p.read_bytes().replace(b'\r\n',b'')]; print('ERROR: Los scripts batch deben usar CRLF: ' + ', '.join(bad) if bad else '', end=''); raise SystemExit(1 if bad else 0)"
if errorlevel 1 exit /b 1

exit /b 0
