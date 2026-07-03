"""
Filament color database for the 3D Print Color Palette Matcher.

Each filament entry is a dict with the following keys:
    brand    : Manufacturer name (e.g. "Bambu Lab")
    material : Material type ("PLA", "ABS" or "PETG")
    name     : Marketing color name (e.g. "Bambu Green")
    hex      : HEX color string, e.g. "#00AE42"
    url      : Purchase / product URL

The RGB tuple is derived automatically from the HEX value via ``get_filaments``
so the data below only has to store the HEX string.

The palette values are approximations of the real-world filament colors and are
meant for visual matching, not for exact color reproduction.
"""

from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Raw filament data grouped roughly by brand for readability.
# ---------------------------------------------------------------------------
_FILAMENTS: List[Dict[str, str]] = [
    # ------------------------------------------------------------------ #
    # Bambu Lab (great for AMS multi-color systems)                      #
    # ------------------------------------------------------------------ #
    {"brand": "Bambu Lab", "material": "PLA", "name": "Jade White", "hex": "#FFFFFF", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Black", "hex": "#000000", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Bambu Green", "hex": "#00AE42", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Bambu Red", "hex": "#C12E1F", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Blue", "hex": "#0A2989", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Sunflower Yellow", "hex": "#FEC600", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Orange", "hex": "#FF6A13", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Cyan", "hex": "#0086D6", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Magenta", "hex": "#EC008C", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Purple", "hex": "#5E43B7", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Gray", "hex": "#8E9089", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Silver", "hex": "#A6A9AA", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Gold", "hex": "#E4BD68", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Brown", "hex": "#7C4B00", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Pink", "hex": "#F55A74", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PETG", "name": "PETG Black", "hex": "#000000", "url": "https://us.store.bambulab.com/products/petg-hf"},
    {"brand": "Bambu Lab", "material": "PETG", "name": "PETG White", "hex": "#F5F5F5", "url": "https://us.store.bambulab.com/products/petg-hf"},
    {"brand": "Bambu Lab", "material": "PETG", "name": "PETG Green", "hex": "#00A651", "url": "https://us.store.bambulab.com/products/petg-hf"},
    {"brand": "Bambu Lab", "material": "PETG", "name": "PETG Blue", "hex": "#1B5BA0", "url": "https://us.store.bambulab.com/products/petg-hf"},
    {"brand": "Bambu Lab", "material": "PETG", "name": "PETG Red", "hex": "#BB1A22", "url": "https://us.store.bambulab.com/products/petg-hf"},
    {"brand": "Bambu Lab", "material": "ABS", "name": "ABS Black", "hex": "#0A0A0A", "url": "https://us.store.bambulab.com/products/abs"},
    {"brand": "Bambu Lab", "material": "ABS", "name": "ABS White", "hex": "#F2F2F2", "url": "https://us.store.bambulab.com/products/abs"},
    {"brand": "Bambu Lab", "material": "ABS", "name": "ABS Blue", "hex": "#0057A6", "url": "https://us.store.bambulab.com/products/abs"},
    {"brand": "Bambu Lab", "material": "ABS", "name": "ABS Red", "hex": "#D3122A", "url": "https://us.store.bambulab.com/products/abs"},

    # ------------------------------------------------------------------ #
    # Hatchbox                                                           #
    # ------------------------------------------------------------------ #
    {"brand": "Hatchbox", "material": "PLA", "name": "White", "hex": "#F7F7F4", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Black", "hex": "#1A1A1A", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "True Red", "hex": "#B01B22", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Blue", "hex": "#1F4E9B", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Green", "hex": "#2E8B57", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Yellow", "hex": "#F2C50B", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Orange", "hex": "#E8641A", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Purple", "hex": "#6A3FA0", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Gray", "hex": "#7D7F7C", "url": "https://www.hatchbox3d.com/collections/pla"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Black", "hex": "#151515", "url": "https://www.hatchbox3d.com/collections/petg"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG White", "hex": "#FAFAFA", "url": "https://www.hatchbox3d.com/collections/petg"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Red", "hex": "#A5202A", "url": "https://www.hatchbox3d.com/collections/petg"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Blue", "hex": "#22548F", "url": "https://www.hatchbox3d.com/collections/petg"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS Black", "hex": "#181818", "url": "https://www.hatchbox3d.com/collections/abs"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS White", "hex": "#F4F4F0", "url": "https://www.hatchbox3d.com/collections/abs"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS Red", "hex": "#AE1C24", "url": "https://www.hatchbox3d.com/collections/abs"},

    # ------------------------------------------------------------------ #
    # Prusament                                                          #
    # ------------------------------------------------------------------ #
    {"brand": "Prusament", "material": "PLA", "name": "Vanilla White", "hex": "#EFE8D8", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Galaxy Black", "hex": "#1C1C22", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Lipstick Red", "hex": "#B5182B", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Ocean Blue", "hex": "#0067A5", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Prusa Orange", "hex": "#F05A22", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Pineapple Yellow", "hex": "#F6BE00", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Mint", "hex": "#4FB99A", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PLA", "name": "Gravity Grey", "hex": "#5A5D5E", "url": "https://www.prusa3d.com/category/prusament-pla/"},
    {"brand": "Prusament", "material": "PETG", "name": "Jet Black", "hex": "#121212", "url": "https://www.prusa3d.com/category/prusament-petg/"},
    {"brand": "Prusament", "material": "PETG", "name": "Signal White", "hex": "#F1F1EC", "url": "https://www.prusa3d.com/category/prusament-petg/"},
    {"brand": "Prusament", "material": "PETG", "name": "Prusa Orange", "hex": "#F0501E", "url": "https://www.prusa3d.com/category/prusament-petg/"},
    {"brand": "Prusament", "material": "PETG", "name": "Urban Grey", "hex": "#6C6E70", "url": "https://www.prusa3d.com/category/prusament-petg/"},
    {"brand": "Prusament", "material": "ABS", "name": "Prusa Orange", "hex": "#F05622", "url": "https://www.prusa3d.com/category/prusament-asa/"},

    # ------------------------------------------------------------------ #
    # eSun                                                               #
    # ------------------------------------------------------------------ #
    {"brand": "eSun", "material": "PLA", "name": "Cold White", "hex": "#F8F8F5", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Solid Black", "hex": "#101010", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Fire Engine Red", "hex": "#C0202B", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Blue", "hex": "#1857A6", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Green", "hex": "#3AA935", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Yellow", "hex": "#F5C518", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Orange", "hex": "#EE6A1D", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Grey", "hex": "#808285", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PLA", "name": "Pink", "hex": "#EE6E9E", "url": "https://www.esun3d.com/pla-pro-product/"},
    {"brand": "eSun", "material": "PETG", "name": "PETG Solid Black", "hex": "#141414", "url": "https://www.esun3d.com/petg-product/"},
    {"brand": "eSun", "material": "PETG", "name": "PETG White", "hex": "#F6F6F2", "url": "https://www.esun3d.com/petg-product/"},
    {"brand": "eSun", "material": "PETG", "name": "PETG Red", "hex": "#BE2230", "url": "https://www.esun3d.com/petg-product/"},
    {"brand": "eSun", "material": "PETG", "name": "PETG Blue", "hex": "#1E5DA8", "url": "https://www.esun3d.com/petg-product/"},
    {"brand": "eSun", "material": "ABS", "name": "ABS Black", "hex": "#111111", "url": "https://www.esun3d.com/abs-product/"},
    {"brand": "eSun", "material": "ABS", "name": "ABS White", "hex": "#F5F5F0", "url": "https://www.esun3d.com/abs-product/"},
    {"brand": "eSun", "material": "ABS", "name": "ABS Green", "hex": "#37A63E", "url": "https://www.esun3d.com/abs-product/"},

    # ------------------------------------------------------------------ #
    # Polymaker                                                          #
    # ------------------------------------------------------------------ #
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Cotton White", "hex": "#F2EFE9", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Charcoal Black", "hex": "#26262A", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Army Red", "hex": "#9E2B25", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Sapphire Blue", "hex": "#1D4E89", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Forest Green", "hex": "#2C6E49", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyLite Yellow", "hex": "#F4C20D", "url": "https://polymaker.com/product/polylite-pla/"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Muted Grey", "hex": "#8A8D8F", "url": "https://polymaker.com/product/polyterra-pla/"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG Black", "hex": "#161616", "url": "https://polymaker.com/product/polylite-petg/"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG White", "hex": "#F7F7F3", "url": "https://polymaker.com/product/polylite-petg/"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG Teal", "hex": "#008C99", "url": "https://polymaker.com/product/polylite-petg/"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS Black", "hex": "#131313", "url": "https://polymaker.com/product/polylite-abs/"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS White", "hex": "#F4F4EF", "url": "https://polymaker.com/product/polylite-abs/"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS Orange", "hex": "#EC6B1F", "url": "https://polymaker.com/product/polylite-abs/"},

    # ------------------------------------------------------------------ #
    # Overture                                                           #
    # ------------------------------------------------------------------ #
    {"brand": "Overture", "material": "PLA", "name": "White", "hex": "#F6F6F3", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PLA", "name": "Black", "hex": "#171717", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PLA", "name": "Red", "hex": "#C21F2A", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PLA", "name": "Blue", "hex": "#215FA6", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PLA", "name": "Green", "hex": "#2F9E44", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PLA", "name": "Space Grey", "hex": "#6E7175", "url": "https://overture3d.com/collections/pla-filament"},
    {"brand": "Overture", "material": "PETG", "name": "PETG Black", "hex": "#141414", "url": "https://overture3d.com/collections/petg-filament"},
    {"brand": "Overture", "material": "PETG", "name": "PETG White", "hex": "#F8F8F4", "url": "https://overture3d.com/collections/petg-filament"},

    # ------------------------------------------------------------------ #
    # SUNLU                                                              #
    # ------------------------------------------------------------------ #
    {"brand": "SUNLU", "material": "PLA", "name": "White", "hex": "#F7F7F5", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PLA", "name": "Black", "hex": "#131313", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PLA", "name": "Red", "hex": "#C31C28", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PLA", "name": "Sky Blue", "hex": "#2C9BD6", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PLA", "name": "Grass Green", "hex": "#3BA935", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PLA", "name": "Yellow", "hex": "#F6C90E", "url": "https://www.sunlu.com/collections/pla-filament"},
    {"brand": "SUNLU", "material": "PETG", "name": "PETG Grey", "hex": "#75787B", "url": "https://www.sunlu.com/collections/petg-filament"},
]


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert a ``#RRGGBB`` string to an ``(r, g, b)`` int tuple."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def get_filaments() -> List[Dict]:
    """Return the full filament list with an added ``rgb`` tuple for each entry."""
    filaments = []
    for entry in _FILAMENTS:
        item = dict(entry)
        item["rgb"] = _hex_to_rgb(entry["hex"])
        filaments.append(item)
    return filaments


def get_brands() -> List[str]:
    """Return a sorted list of unique brand names."""
    return sorted({f["brand"] for f in _FILAMENTS})


def get_materials() -> List[str]:
    """Return a sorted list of unique material types."""
    return sorted({f["material"] for f in _FILAMENTS})


if __name__ == "__main__":
    fils = get_filaments()
    print(f"Total filaments: {len(fils)}")
    print(f"Brands: {', '.join(get_brands())}")
    print(f"Materials: {', '.join(get_materials())}")
