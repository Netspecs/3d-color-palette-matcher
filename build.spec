# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the 3D Print Color Palette Matcher.

Build a standalone one-file executable:

    pip install pyinstaller
    pyinstaller build.spec

The result appears in the ``dist/`` folder:
    * Windows : dist/3DColorPaletteMatcher.exe
    * macOS   : dist/3DColorPaletteMatcher
    * Linux   : dist/3DColorPaletteMatcher

tkinterdnd2 ships a small Tcl library that must be bundled for drag & drop to
keep working in the frozen app; we collect it automatically below.
"""

import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

datas = []
binaries = []
hiddenimports = ["PIL._tkinter_finder"]

# Bundle tkinterdnd2's Tcl assets if the package is installed.
try:
    datas += collect_data_files("tkinterdnd2")
    binaries += collect_dynamic_libs("tkinterdnd2")
    hiddenimports.append("tkinterdnd2")
except Exception:
    pass

# Bundle the app icon (PNG) so the running window can display it on every OS.
if os.path.exists(os.path.join("docs", "icon.png")):
    datas += [(os.path.join("docs", "icon.png"), "docs")]

# Pick the right icon format for the platform being built on:
#   Windows -> .ico   |   macOS -> .icns   |   Linux -> PNG (or none)
if sys.platform.startswith("win"):
    _icon = os.path.join("docs", "icon.ico")
elif sys.platform == "darwin":
    _icon = os.path.join("docs", "icon.icns")
else:
    _icon = os.path.join("docs", "icon.png")
app_icon = _icon if os.path.exists(_icon) else None


a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="3DColorPaletteMatcher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app — no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,
)

# On macOS, wrap the binary in a proper .app bundle so it gets a Dock icon
# and shows up like a native application.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="3D Color Palette Matcher.app",
        icon=app_icon,
        bundle_identifier="com.netspecs.colorpalettematcher",
    )
