# Changelog

All notable changes to the 3D Print Color Palette Matcher project.

## [v1.0] - 2026-07-05

### 🎨 App Icon & Desktop Integration (PR #2)
- **Custom app icon** with 3D filament spool + rainbow color arc design
- Platform-specific icon formats:
  - Windows: `.ico` (multi-resolution)
  - macOS: `.icns` (1.1MB robust ICNS)
  - Linux: `.png` (256x256)
- Icon embedded in all executables (shows on desktop/taskbar/dock)
- Desktop shortcut installers:
  - `install/windows-create-desktop-shortcut.bat` (PowerShell script)
  - `install/linux-install.sh` (creates .desktop launcher)
  - `install/README.md` (installation instructions)

### 🔗 Purchase Link Fixes (PR #3)
Fixed broken "Buy" buttons for 6 brands (44 filament entries):
- **Hatchbox** → Amazon store page (official site blocks API access)
- **Amazon Basics** → Amazon search (product discontinued)
- **Atomic Filament** → Official store homepage
- **3D Solutech** → Amazon search (official site unreliable)
- **Inland** → Micro Center filament page (cleaned malformed URLs)
- **Polymaker** → Official shop.polymaker.com

All purchase links now work correctly when clicked by users.

### 🚀 Major Features (PR #1)
- **Standalone executables** for Windows, macOS, and Linux (PyInstaller)
- **Expanded filament database**: 145 filaments across 16 brands
  - Bambu Lab, Snapmaker, Polymaker, Hatchbox, Prusament, Overture, eSUN, SUNLU, etc.
  - Real pricing data for cost estimation
- **Cost calculator** (`cost.py`) - estimates print cost based on palette
- **Save/Load palettes** (`palette_store.py`) - JSON format
- **Slicer export** (`slicer_export.py`) - 6 formats:
  - CSV, TXT, JSON, GPL (GIMP), INI (PrusaSlicer), ASE (Adobe Swatch)
- **Brightness/saturation sliders** - fine-tune color extraction
- **GitHub Actions CI/CD** - auto-builds executables on every merge
- **Documentation**: README with badges, demo GIF, screenshot
- **Contributing guide** (CONTRIBUTING.md)
- **MIT License** (LICENSE)

### 📦 Initial Release
- Core color extraction using k-means clustering
- CIE76 Delta E color matching (perceptually accurate)
- Filter by brand and material type
- Top-3 filament match suggestions
- Modern dark UI with Tkinter
- Cross-platform compatibility

---

## Download

**Latest Release**: [v1.0](https://github.com/Netspecs/3d-color-palette-matcher/releases/tag/v1.0)

- ✅ Windows (30 MB) - `3DColorPaletteMatcher-windows.exe`
- ✅ macOS (20 MB) - `3DColorPaletteMatcher-macos`
- ✅ Linux (47 MB) - `3DColorPaletteMatcher-linux`

All executables include the custom icon and working purchase links.
