#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "ERROR: setup.sh solo puede ejecutarse en Linux."
    exit 1
fi

run_privileged() {
    if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        echo "ERROR: Se requieren privilegios administrativos para instalar dependencias del sistema."
        exit 1
    fi
}

if [[ "${LECTORCITO_SKIP_SYSTEM_PACKAGES:-0}" != "1" ]]; then
    if command -v apt-get >/dev/null 2>&1; then
        run_privileged apt-get update
        run_privileged apt-get install -y python3 python3-venv python3-tk python3-dev build-essential patchelf ccache xdg-utils desktop-file-utils
    elif command -v pacman >/dev/null 2>&1; then
        run_privileged pacman -S --needed --noconfirm python tk base-devel patchelf ccache xdg-utils desktop-file-utils
    else
        echo "ERROR: Distribución no soportada automáticamente. Instale Python 3, Tk, un compilador C/C++, patchelf y ccache."
        exit 1
    fi
fi

if [[ "${LECTORCITO_SYSTEM_ONLY:-0}" == "1" ]]; then
    echo "Dependencias del sistema Linux listas."
    exit 0
fi

PYTHON_BIN="${PYTHON_BIN:-python3}"
RUNTIME_REQ="$PROJECT_ROOT/requirements/linux.txt"
BUILD_REQ="$PROJECT_ROOT/requirements/build.txt"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "ERROR: No se encontró $PYTHON_BIN."
    exit 1
fi
if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if (3, 11) <= sys.version_info[:2] < (3, 14) else 1)' >/dev/null 2>&1; then
    echo "ERROR: Se requiere Python 3.11, 3.12 o 3.13."
    exit 1
fi

"$PYTHON_BIN" -m venv .venv-linux
".venv-linux/bin/python" -m pip install --upgrade pip setuptools wheel
".venv-linux/bin/python" -m pip install -r "$RUNTIME_REQ" -r "$BUILD_REQ" --default-timeout=100
".venv-linux/bin/python" - <<'PY'
import tkinter
import customtkinter
import appdirs
import PIL
print("Entorno Linux listo.")
PY
