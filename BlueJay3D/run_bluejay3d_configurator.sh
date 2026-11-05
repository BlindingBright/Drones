#!/usr/bin/env bash
# Bluejay3D Configurator Easy Launcher
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use project venv python if available, else system python3
if [ -f "$DIR/3d-whoop-tuning/.venv/bin/python" ]; then
    PY="$DIR/3d-whoop-tuning/.venv/bin/python"
elif [ -f "$DIR/.venv/bin/python" ]; then
    PY="$DIR/.venv/bin/python"
else
    PY="python3"
fi

exec "$PY" "$DIR/launch_bluejay3d_configurator.py" "$@"
