@echo off
REM =====================================================================
REM  3D Color Palette Matcher - create a Desktop shortcut (Windows)
REM
REM  HOW TO USE:
REM   1. Put this .bat file in the SAME folder as
REM      3DColorPaletteMatcher-windows.exe
REM   2. Double-click this .bat file.
REM   3. A shortcut (with the app icon) appears on your Desktop.
REM =====================================================================

setlocal
set "EXE=%~dp03DColorPaletteMatcher-windows.exe"

if not exist "%EXE%" (
    echo Could not find 3DColorPaletteMatcher-windows.exe next to this file.
    echo Please keep this .bat in the same folder as the .exe and try again.
    pause
    exit /b 1
)

set "SHORTCUT=%USERPROFILE%\Desktop\3D Color Palette Matcher.lnk"

powershell -NoProfile -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT%');" ^
  "$s.TargetPath='%EXE%';" ^
  "$s.WorkingDirectory=Split-Path '%EXE%';" ^
  "$s.IconLocation='%EXE%,0';" ^
  "$s.Description='Extract colors from an image and match them to 3D printing filaments';" ^
  "$s.Save()"

echo.
echo Done! A "3D Color Palette Matcher" icon is now on your Desktop.
pause
