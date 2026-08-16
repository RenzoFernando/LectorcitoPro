#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "ERROR: buildlinux.sh solo puede ejecutarse en Linux."
    exit 1
fi

PYTHON_BIN="$PROJECT_ROOT/.venv-linux/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "ERROR: No existe .venv-linux. Ejecute primero ./setupLinux.sh."
    exit 1
fi

ENTRY_POINT="$PROJECT_ROOT/src/main.py"
OUTPUT_DIR="$PROJECT_ROOT/downloads"
BUILD_ROOT="$PROJECT_ROOT/build/linux"

if [[ ! -f "$ENTRY_POINT" ]]; then
    echo "ERROR: No se encontró $ENTRY_POINT."
    exit 1
fi

LINUX_EXECUTABLE_NAME="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_LINUX_EXECUTABLE_NAME)')"
LINUX_PACKAGE_DIR_NAME="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_LINUX_PACKAGE_DIR_NAME)')"
LINUX_ARTIFACT_NAME="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_LINUX_ARTIFACT_NAME)')"
ICON_RELATIVE_PATH="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_ICON_PNG_RELATIVE_PATH)')"
ICON_FILE="$PROJECT_ROOT/$ICON_RELATIVE_PATH"

if [[ ! -f "$ICON_FILE" ]]; then
    echo "ERROR: No se encontró $ICON_FILE."
    exit 1
fi

rm -rf "$BUILD_ROOT"
mkdir -p "$BUILD_ROOT" "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME"

"$PYTHON_BIN" -m nuitka \
    --mode=standalone \
    --assume-yes-for-downloads \
    --enable-plugin=tk-inter \
    --include-package=customtkinter \
    --include-package-data=customtkinter \
    --include-data-dir="$PROJECT_ROOT/resources=resources" \
    --linux-icon="$ICON_FILE" \
    --nofollow-import-to=win32com \
    --nofollow-import-to=pythoncom \
    --nofollow-import-to=pywintypes \
    --output-filename="$LINUX_EXECUTABLE_NAME" \
    --output-dir="$BUILD_ROOT" \
    --remove-output \
    "$ENTRY_POINT"

DIST_DIR="$(find "$BUILD_ROOT" -maxdepth 1 -type d -name '*.dist' -print -quit)"
if [[ -z "$DIST_DIR" || ! -d "$DIST_DIR" ]]; then
    echo "ERROR: Nuitka no generó el directorio standalone esperado."
    exit 1
fi

PACKAGE_DIR="$BUILD_ROOT/$LINUX_PACKAGE_DIR_NAME"
rm -rf "$PACKAGE_DIR"
mv "$DIST_DIR" "$PACKAGE_DIR"

if [[ -f "$PROJECT_ROOT/LICENSE" ]]; then
    cp "$PROJECT_ROOT/LICENSE" "$PACKAGE_DIR/LICENSE"
fi

if [[ ! -x "$PACKAGE_DIR/$LINUX_EXECUTABLE_NAME" ]]; then
    chmod +x "$PACKAGE_DIR/$LINUX_EXECUTABLE_NAME"
fi

tar -C "$BUILD_ROOT" -czf "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME" "$LINUX_PACKAGE_DIR_NAME"

if [[ ! -s "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME" ]]; then
    echo "ERROR: No se pudo generar el artefacto Linux."
    exit 1
fi

echo "Artefacto Linux generado correctamente:"
echo "$OUTPUT_DIR/$LINUX_ARTIFACT_NAME"
