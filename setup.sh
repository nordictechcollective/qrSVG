#!/bin/bash

set -eou pipefail

# Create Virtual Environment if needed
if [ ! -d ".venv" ]; then
    python3.12 -m venv .venv --prompt "qrSVG"
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -e .[dev]
fi

# Activate Virtual Environment
. .venv/bin/activate

# Add diff for our svg files (see pyproject.toml and .gitattributes)
git config --local diff.qrsvg.textconv "qrsvg-meta"
git config --local diff.qrsvg.binary true
