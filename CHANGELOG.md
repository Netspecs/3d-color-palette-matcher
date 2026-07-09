# Changelog

All notable changes to the 3D Print Color Palette Matcher project.

## [v2.0] - 2026-07-09

### 🎯 More accurate color matching
- Switched filament matching from **CIE76** to **CIEDE2000 (ΔE2000)** — the
  current CIE-standard perceptual color-difference formula. Matches now line up
  much better with how the human eye actually sees color.
- Recalibrated the match-quality scale for ΔE2000:
  `≤1 perfect · ≤2 excellent · ≤3.5 great · ≤6 good · ≤10 fair · >10 approximate`.

### 🧵 Bigger, honest filament database
- Grew the database from **145 → 225 filaments** and added the material lines the
  marketing always claimed: **TPU, Silk, Matte and Wood** (alongside PLA/PETG/ABS)
  from Bambu Lab, Polymaker, eSun, SUNLU, Overture and ColorFabb.
- Added retail price data (and material-level fallbacks) for all new materials.

### 🎨 Enter colors directly (no image needed)
- New **"Enter Colors"** dialog: paste/type hex codes or use a color picker and
  match straight to filaments — great when you already have brand colors or a
  palette in mind.

### 🖨️ Print System Planner
- New planner assigns your matched colors to filament **slots** for:
  **Bambu AMS (4 / 8 / 16), Prusa MMU3 (5), tool changers / multi-head (custom,
  up to 8), IDEX / dual (2), and manual filament swaps**.
- Flags colors that don't fit the available slots and shows **purge/waste
  guidance** only for shared-nozzle systems (AMS, MMU3).

### 🖼️ Filament preview
- New **Filament Preview** re-renders your image using the best-match filament
  color for each palette color (posterized), so you can see roughly how the print
  will look — and save the preview as a PNG/JPG.

### 🏷️ Misc
- Version bumped to **2.0** (app + Windows installer).
- Updated README / docs to match the real feature set and database.

## [v1.0] - 2026-07-05

### 🔧 Windows Installer (PR #4)
- **Proper Windows installer** built with Inno Setup (`3DColorPaletteMatcher-Setup.exe`)
- Creates a **desktop icon** with the custom app logo automatically
- Adds a **Start Menu** shortcut
- Registers an **uninstaller** in **Settings → Apps** ("Programs and Features")
- Installs per-user (no admin rights required)
- Portable versions still available for all platforms (`Portable-*.exe`/`Portable-*`)

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
