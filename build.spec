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
    icon="docs/icon.ico" if __import__("os").path.exists("docs/icon.ico") else None,
)
