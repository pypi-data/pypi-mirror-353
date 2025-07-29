#!/bin/bash
set -euxo pipefail

# Development setup following JupyterLab extension examples
echo "Setting up jupyter-session-tracer for development..."

# Create yarn.lock if it doesn't exist
touch yarn.lock

# Install Python package in development mode
echo "Installing Python package in development mode..."
pip install -e .

# Install/link the extension for development
echo "Installing extension for development..."
jupyter labextension develop . --overwrite

# Build the extension
echo "Building extension..."
jlpm run build

echo "Development setup complete!"
echo "To start development:"
echo "1. In one terminal: jlpm watch"
echo "2. In another terminal: jupyter lab"
echo "3. Refresh your browser after making changes" 