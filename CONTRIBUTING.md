# Contributing

Thanks for your interest in improving the **3D Print Color Palette Matcher**! 🎨🖨️

Contributions of all sizes are welcome — from fixing a typo to adding a whole
new filament brand.

## Ways to help

### 1. Add filament colors (easiest — no coding needed!)
The most valuable contribution is keeping the filament database accurate and
growing it. Open [`filament_database.py`](filament_database.py) and add entries
to the `_FILAMENTS` list:

```python
{"brand": "Your Brand", "material": "PLA", "name": "Color Name",
 "hex": "#RRGGBB", "url": "https://where-to-buy"},
```

Tips:
- Grab the HEX value from the manufacturer's product photo or swatch.
- Use `"PLA"`, `"PETG"` or `"ABS"` for `material`.
- Optionally add a price in `_PRICE_PER_KG` as `"Your Brand|PLA": 19.99`.

### 2. Report bugs / request features
Open an [issue](../../issues) describing what happened and what you expected.
Screenshots help a lot.

### 3. Code contributions
1. Fork the repo and create a branch: `git checkout -b my-feature`
2. Make your change.
3. Run a quick sanity check:
   ```bash
   python -m py_compile app.py color_utils.py filament_database.py cost.py palette_store.py slicer_export.py
   python filament_database.py   # prints filament / brand counts
   ```
4. Commit and open a Pull Request against `main`.

## Project layout
| File | Purpose |
|------|---------|
| `app.py` | Tkinter GUI |
| `color_utils.py` | Color extraction (k-means) + Lab/Delta-E matching |
| `filament_database.py` | Filament colors, prices, brands |
| `cost.py` | Filament cost estimation |
| `palette_store.py` | Saving/loading favorite palettes |
| `slicer_export.py` | CSV / GIMP / slicer-config exports |

## Code style
- Standard library + Pillow + NumPy only for core logic (keep it lightweight).
- Keep functions documented with short docstrings.
- No hard tabs; 4-space indentation.

Happy printing! 🚀
