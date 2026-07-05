@echo off
REM ============================================================
REM  Build a standalone Windows .exe for the Color Palette Matcher
REM  Double-click this file (or run it from a command prompt).
REM ============================================================

echo Installing build dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo.
echo Building executable (this can take a minute)...
python -m PyInstaller build.spec --noconfirm

echo.
echo ============================================================
echo  Done! Your app is here:
echo    dist\3DColorPaletteMatcher.exe
echo  Double-click it to run - no Python required.
echo ============================================================
pause
