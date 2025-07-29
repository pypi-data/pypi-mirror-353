#!/usr/bin/env python3
"""
Setup script for jupyter-session-tracer
"""

import os
import shutil
from pathlib import Path
from setuptools import setup, find_packages

# Read version from _version.py
version_file = Path(__file__).parent / "jupyter_session_tracer" / "_version.py"
version = {}
if version_file.exists():
    with open(version_file) as f:
        exec(f.read(), version)
    __version__ = version.get("__version__", "0.1.0")
else:
    __version__ = "0.1.0"

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

# Ensure labextension is built
labext_dir = Path(__file__).parent / "jupyter_session_tracer" / "labextension"
if not labext_dir.exists():
    print("Warning: labextension directory not found. Run 'jupyter labextension build .' first.")

setup(
    name="jupyter-session-tracer",
    version=__version__,
    description="A JupyterLab extension that displays session information in a beautiful popup",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-username/jupyter-session-tracer",
    license="BSD-3-Clause",
    platforms="Linux, Mac OS X, Windows",
    keywords=["jupyter", "jupyterlab", "jupyterlab-extension"],
    classifiers=[
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 4",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
        "Framework :: Jupyter :: JupyterLab :: Extensions :: Prebuilt",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "jupyter_server>=2.0.1,<3",
    ],
    include_package_data=True,
    package_data={
        "jupyter_session_tracer": [
            "labextension/**/*",
        ],
    },
    data_files=[
        (
            "share/jupyter/labextensions/jupyter-session-tracer",
            [
                "install.json",
            ],
        ),
    ],
    zip_safe=False,
) 