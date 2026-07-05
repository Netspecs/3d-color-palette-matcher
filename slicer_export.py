"""
Export helpers that turn a matched palette into formats useful for slicers
and other design tools.

Supported outputs:
    * CSV .......... universal spreadsheet-friendly table.
    * GIMP palette . ``.gpl`` file readable by GIMP, Inkscape, Krita, etc.
    * Slicer config  ``filament_colour`` snippet for PrusaSlicer / OrcaSlicer /
                     Bambu Studio (all Slic3r-derived and share this key).
    * Hex list ..... plain ``#RRGGBB`` per line, handy for Cura and manual use.

Each function takes ``results`` — a list of ``(color, matches)`` tuples as
produced by the app — and returns a string ready to be written to disk.
"""

from typing import Dict, List, Tuple

Result = Tuple[Dict, List[Dict]]


def _best(matches: List[Dict]) -> Dict:
    return matches[0] if matches else {}


def to_csv(results: List[Result]) -> str:
    """Return the palette as CSV text (best match per color plus alternates)."""
    import csv
    import io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "color_index", "image_hex", "image_rgb", "percentage",
        "match_rank", "brand", "material", "filament_name",
        "filament_hex", "delta_e", "price_per_kg", "url",
    ])
    for idx, (color, matches) in enumerate(results, start=1):
        if not matches:
            writer.writerow([idx, color["hex"], _rgb_str(color["rgb"]),
                             color["percentage"], "", "", "", "(no match)",
                             "", "", "", ""])
            continue
        for rank, m in enumerate(matches, start=1):
            writer.writerow([
                idx, color["hex"], _rgb_str(color["rgb"]), color["percentage"],
                rank, m["brand"], m["material"], m["name"], m["hex"],
                m.get("distance", ""), m.get("price_per_kg", ""), m["url"],
            ])
    return buf.getvalue()


def to_gpl(results: List[Result], name: str = "3D Print Palette") -> str:
    """Return a GIMP ``.gpl`` palette (uses the best filament match per color)."""
    lines = ["GIMP Palette", f"Name: {name}", "Columns: 4", "#"]
    for idx, (color, matches) in enumerate(results, start=1):
        best = _best(matches)
        rgb = best.get("rgb", color["rgb"])
        label = (f"{best['brand']} {best['name']}" if best
                 else f"Color {idx} {color['hex']}")
        r, g, b = rgb
        lines.append(f"{r:>3} {g:>3} {b:>3}\t{label}")
    return "\n".join(lines) + "\n"


def to_slicer_config(results: List[Result]) -> str:
    """
    Return a ``filament_colour`` config snippet for PrusaSlicer / OrcaSlicer /
    Bambu Studio. Paste the line into an exported config, or use the hex codes
    directly in the slicer's filament color pickers (one per AMS slot).
    """
    hexes = []
    for color, matches in results:
        best = _best(matches)
        hexes.append(best.get("hex", color["hex"]))
    joined = ";".join(hexes)
    header = (
        "# Filament colors for PrusaSlicer / OrcaSlicer / Bambu Studio\n"
        "# Assign these to your AMS / extruder slots in order.\n"
        f"# {len(hexes)} color(s).\n"
    )
    return header + f"filament_colour = {joined}\n"


def to_hex_list(results: List[Result]) -> str:
    """Return one ``#RRGGBB`` per line (best match per color)."""
    out = []
    for color, matches in results:
        best = _best(matches)
        out.append(best.get("hex", color["hex"]))
    return "\n".join(out) + "\n"


def _rgb_str(rgb) -> str:
    r, g, b = rgb
    return f"{r},{g},{b}"


# Maps a lowercase file extension to (writer function, description).
EXPORTERS = {
    ".csv": (to_csv, "CSV spreadsheet"),
    ".gpl": (to_gpl, "GIMP/Inkscape palette"),
    ".ini": (to_slicer_config, "Slicer filament config"),
    ".txt": (to_hex_list, "Hex list"),
}


def export_to_file(path: str, results: List[Result]) -> str:
    """
    Write ``results`` to ``path`` choosing the format from the file extension.

    Returns a short description of the format written. Raises ``ValueError`` for
    unsupported extensions.
    """
    import os
    ext = os.path.splitext(path)[1].lower()
    if ext not in EXPORTERS:
        raise ValueError(f"Unsupported export type: {ext}")
    func, desc = EXPORTERS[ext]
    if func is to_gpl:
        content = func(results, name=os.path.splitext(os.path.basename(path))[0])
    else:
        content = func(results)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return desc
