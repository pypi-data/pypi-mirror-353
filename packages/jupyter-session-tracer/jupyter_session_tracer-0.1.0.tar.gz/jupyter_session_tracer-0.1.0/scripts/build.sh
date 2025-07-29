#!/bin/bash
set -euxo pipefail

# Build the extension following JupyterLab extension examples
echo "Building jupyter-session-tracer extension..."

# Clean previous builds
echo "Cleaning previous builds..."
jlpm clean:all

# Install dependencies
echo "Installing dependencies..."
jlpm install

# Build TypeScript source
echo "Building TypeScript source..."
jlpm build:lib:prod

# Build the JupyterLab extension
echo "Building JupyterLab extension..."
jlpm build:labextension

echo "Build complete! Extension built in jupyter_session_tracer/labextension/" 