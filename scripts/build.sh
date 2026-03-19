#!/usr/bin/env bash
# PyInstaller build script for metadexer standalone executables.
# Specification reference: metadexer-spec.md §18.2 (Build and Release Pipeline).
# Usage: ./scripts/build.sh
set -euo pipefail

VERSION=$(python3 -c "from metadexer._version import __version__; print(__version__)")
echo "Building metadexer v${VERSION}..."

pyinstaller \
    --name "metadexer" \
    --onefile \
    --console \
    --clean \
    src/metadexer/cli.py

echo "Build complete. Artifact: dist/metadexer"
