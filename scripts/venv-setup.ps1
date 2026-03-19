$ErrorActionPreference = "Stop"

$VenvDir = ".venv"

if (Test-Path $VenvDir) {
    Write-Host "Virtual environment already exists at $VenvDir"
} else {
    python -m venv $VenvDir
    Write-Host "Created virtual environment at $VenvDir"
}

& "$VenvDir\Scripts\Activate.ps1"
pip install --upgrade pip --quiet
pip install -e ".[dev]" --quiet
Write-Host "Development dependencies installed."
