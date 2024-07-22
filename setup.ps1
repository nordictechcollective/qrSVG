# Create a Virtual Environment if needed
if (-not (Test-Path .venv)) {
    winget install Python.Python.3.12
    py -3.12 -m venv .venv --prompt qrSVG
    .venv\Scripts\pip install --upgrade pip
    .venv\Scripts\pip install -e .[dev]
}

# Activate the Virtual Environment
.venv\Scripts\Activate.ps1

# Add diff for our svg files (see pyproject.toml and .gitattributes)
git config --local diff.qrsvg-diff.textconv "qrsvg-meta"
git config --local diff.qrsvg-diff.binary true
