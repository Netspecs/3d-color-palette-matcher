#!/usr/bin/env bash
# ============================================================
#  Build a standalone executable (macOS / Linux)
#  Usage:  bash build_exe.sh
# ============================================================
set -e

echo "Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt pyinstaller

echo
echo "Building executable (this can take a minute)..."
python3 -m PyInstaller build.spec --noconfirm

echo
echo "============================================================"
echo " Done! Your app is here:"
echo "   dist/3DColorPaletteMatcher"
echo " Run it with:  ./dist/3DColorPaletteMatcher"
echo "============================================================"
