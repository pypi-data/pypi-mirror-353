#!/bin/bash
set -euxo pipefail

# Build wheel file for jupyter-session-tracer following JupyterLab extension examples
echo "Building wheel for jupyter-session-tracer..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Install dependencies first (this fixes the lockfile issue)
echo "Installing dependencies..."
jlpm install

# Now clean safely
echo "Cleaning labextension..."
jlpm clean:all

# Build TypeScript source and JupyterLab extension (handled by hatch build hooks)
echo "Building extension using hatch build system..."

# Install build tools
echo "Installing build tools..."
python -m pip install --upgrade build

# Build wheel using modern build system
echo "Building wheel..."
python -m build

echo "Build complete!"
echo "Wheel and source distribution created in dist/ directory:"
ls -la dist/

echo ""
echo "To install the extension:"
echo "  pip install dist/jupyter_session_tracer-*.whl" 