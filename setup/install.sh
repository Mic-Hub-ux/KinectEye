#!/usr/bin/env bash
# Creates .venv in the project root, installs the Python dependencies and
# builds the libfreenect Python binding (not available as a usable pip package).
# Requires the system packages listed in setup/setup_instructions.md.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv"
# libfreenect master as of 2024-01 (Cython 3 compatible wrapper)
LIBFREENECT_COMMIT=09a1f09

for pkg in build-essential git libusb-1.0-0-dev libfreenect-dev; do
    if ! dpkg -s "$pkg" >/dev/null 2>&1; then
        echo "Missing system package: $pkg"
        echo "Run: sudo apt install -y build-essential git libusb-1.0-0-dev libfreenect-dev libfreenect-bin"
        exit 1
    fi
done

python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip setuptools wheel cython
"$VENV/bin/pip" install -r "$ROOT/requirements.txt"

if "$VENV/bin/python" -c "import freenect" 2>/dev/null; then
    echo "freenect binding already installed."
else
    SRC="$(mktemp -d)"
    trap 'rm -rf "$SRC"' EXIT
    git clone -q https://github.com/OpenKinect/libfreenect.git "$SRC/libfreenect"
    git -C "$SRC/libfreenect" checkout -q "$LIBFREENECT_COMMIT"
    # Compile against the headers of the installed libfreenect-dev package.
    CFLAGS="-I/usr/include/libfreenect" \
        "$VENV/bin/pip" install --no-build-isolation "$SRC/libfreenect/wrappers/python"
fi

"$VENV/bin/python" -c "import freenect, cv2, flask; print('All Python modules OK')"
echo
echo "Start the server with:  $VENV/bin/python $ROOT/kinect_streaming/app.py"
