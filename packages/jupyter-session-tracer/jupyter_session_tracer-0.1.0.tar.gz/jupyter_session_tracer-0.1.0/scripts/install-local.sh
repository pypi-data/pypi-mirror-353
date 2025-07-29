#!/bin/bash
set -euxo pipefail

# Install the extension locally without building a wheel
echo "Installing jupyter-session-tracer extension locally..."

# Build TypeScript source
echo "Building TypeScript source..."
npx tsc --sourceMap

# Build the JupyterLab extension
echo "Building JupyterLab extension..."
jupyter labextension build --development True .

# Install Python package in development mode
echo "Installing Python package in development mode..."
pip install -e .

echo "Extension installed successfully!"
echo "You can now start JupyterLab with: jupyter lab" 