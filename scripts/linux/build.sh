#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "ERROR: build.sh solo puede ejecutarse en Linux."
    exit 1
fi

PYTHON_BIN="$PROJECT_ROOT/.venv-linux/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "ERROR: No existe .venv-linux. Ejecuta primero scripts/linux/setup.sh."
    exit 1
fi

if ! "$PYTHON_BIN" -m pip check >/dev/null; then
    echo "ERROR: El entorno Linux tiene dependencias inconsistentes. Ejecuta scripts/linux/setup.sh."
    exit 1
fi
if ! "$PYTHON_BIN" -c 'import appdirs, customtkinter, PIL, nuitka' >/dev/null 2>&1; then
    echo "ERROR: Faltan dependencias Linux. Ejecuta scripts/linux/setup.sh."
    exit 1
fi

ENTRY_POINT="$PROJECT_ROOT/src/main.py"
OUTPUT_DIR="$PROJECT_ROOT/downloads"
BUILD_ROOT="$PROJECT_ROOT/build/linux"

if [[ ! -f "$ENTRY_POINT" ]]; then
    echo "ERROR: No se encontro $ENTRY_POINT."
    exit 1
fi

"$PYTHON_BIN" "$PROJECT_ROOT/src/app_meta.py"

LINUX_ARTIFACT_NAME="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_LINUX_ARTIFACT_NAME)')"
ICON_RELATIVE_PATH="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_ICON_PNG_RELATIVE_PATH)')"
ICON_FILE="$PROJECT_ROOT/$ICON_RELATIVE_PATH"

if [[ ! -f "$ICON_FILE" ]]; then
    echo "ERROR: No se encontro $ICON_FILE."
    exit 1
fi

rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT" "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME"

NUITKA_ARGS=(
    --mode=onefile
    --assume-yes-for-downloads
    --enable-plugin=tk-inter
    --include-package=customtkinter
    --include-package-data=customtkinter
    --include-data-dir="$PROJECT_ROOT/resources=resources"
    --linux-icon="$ICON_FILE"
    --nofollow-import-to=win32com
    --nofollow-import-to=pythoncom
    --nofollow-import-to=pywintypes
    --output-filename="$LINUX_ARTIFACT_NAME"
    --output-dir="$BUILD_ROOT"
    --remove-output
)

if [[ -f "$PROJECT_ROOT/LICENSE" ]]; then
    NUITKA_ARGS+=(--include-data-files="$PROJECT_ROOT/LICENSE=LICENSE")
fi

"$PYTHON_BIN" -m nuitka "${NUITKA_ARGS[@]}" "$ENTRY_POINT"

BUILT_ARTIFACT="$BUILD_ROOT/$LINUX_ARTIFACT_NAME"
if [[ ! -f "$BUILT_ARTIFACT" && -f "$BUILD_ROOT/$LINUX_ARTIFACT_NAME.bin" ]]; then
    BUILT_ARTIFACT="$BUILD_ROOT/$LINUX_ARTIFACT_NAME.bin"
fi

if [[ ! -f "$BUILT_ARTIFACT" ]]; then
    echo "ERROR: Nuitka no genero el binario onefile esperado."
    exit 1
fi

cp "$BUILT_ARTIFACT" "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME"
chmod +x "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME" || true

if [[ ! -s "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME" ]]; then
    echo "ERROR: No se pudo generar el artefacto Linux."
    exit 1
fi

echo "Artefacto Linux portable generado correctamente:"
echo "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME"
