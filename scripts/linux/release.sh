#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

bash "$SCRIPT_DIR/setup.sh"
bash "$SCRIPT_DIR/build.sh"

PYTHON_BIN="$PROJECT_ROOT/.venv-linux/bin/python"
LINUX_ARTIFACT_NAME="$("$PYTHON_BIN" -c 'import os,sys; sys.path.insert(0, os.path.abspath("src")); import app_meta; print(app_meta.APP_LINUX_ARTIFACT_NAME)')"
ARTIFACT="$PROJECT_ROOT/downloads/$LINUX_ARTIFACT_NAME"

if [[ ! -s "$ARTIFACT" ]]; then
    echo "ERROR: No existe el artefacto Linux final."
    exit 1
fi
echo "SHA256 Linux:"
sha256sum "$ARTIFACT"
