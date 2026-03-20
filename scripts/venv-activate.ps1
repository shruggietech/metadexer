$ErrorActionPreference = "Stop"

$VenvDir = (Join-Path -Path $PSScriptRoot -ChildPath "..\.venv")

if (-not (Test-Path $VenvDir)) {
    Write-Error "Virtual environment not found at $VenvDir. Run venv-setup.ps1 first."
    exit 1
}

& "$VenvDir\Scripts\Activate.ps1"
Write-Host "Virtual environment activated."
