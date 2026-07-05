"""
Persistent storage for saved / favorite palettes.

Palettes are stored as JSON in a per-user config directory so they survive
between sessions:

    Windows : %APPDATA%\\3DColorPaletteMatcher\\palettes.json
    macOS   : ~/Library/Application Support/3DColorPaletteMatcher/palettes.json
    Linux   : ~/.config/3DColorPaletteMatcher/palettes.json

Each saved palette has a name, an optional source image name, a timestamp and
the list of extracted colors together with their filament matches.
"""

import json
import os
import time
from typing import Dict, List, Optional

APP_DIR_NAME = "3DColorPaletteMatcher"
STORE_FILENAME = "palettes.json"


def get_config_dir() -> str:
    """Return (and create) the per-user config directory for the app."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif os.sys.platform == "darwin":  # macOS
        base = os.path.expanduser("~/Library/Application Support")
    else:  # Linux / other
        base = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
    path = os.path.join(base, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def _store_path() -> str:
    return os.path.join(get_config_dir(), STORE_FILENAME)


def load_all() -> List[Dict]:
    """Load all saved palettes. Returns an empty list if none exist."""
    path = _store_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _write_all(palettes: List[Dict]) -> None:
    with open(_store_path(), "w", encoding="utf-8") as fh:
        json.dump(palettes, fh, indent=2)


def save_palette(name: str, payload: Dict) -> Dict:
    """
    Save (or overwrite) a palette by name.

    Args:
        name: User-friendly palette name (unique key).
        payload: The palette data (typically the app's export payload).

    Returns:
        The stored palette record.
    """
    name = (name or "Untitled").strip()
    palettes = load_all()
    record = {
        "name": name,
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_image": payload.get("source_image", ""),
        "palette": payload.get("palette", []),
    }
    # Replace an existing palette with the same name, else append.
    for i, p in enumerate(palettes):
        if p.get("name") == name:
            palettes[i] = record
            break
    else:
        palettes.append(record)
    _write_all(palettes)
    return record


def delete_palette(name: str) -> bool:
    """Delete a saved palette by name. Returns True if something was removed."""
    palettes = load_all()
    new_palettes = [p for p in palettes if p.get("name") != name]
    if len(new_palettes) != len(palettes):
        _write_all(new_palettes)
        return True
    return False


def get_palette(name: str) -> Optional[Dict]:
    """Return a saved palette by name, or None if not found."""
    for p in load_all():
        if p.get("name") == name:
            return p
    return None


def list_names() -> List[str]:
    """Return the names of all saved palettes (most recently saved last)."""
    return [p.get("name", "Untitled") for p in load_all()]
