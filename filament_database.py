"""
Filament color database for the 3D Print Color Palette Matcher.

Each filament entry is a dict with the following keys:
    brand    : Manufacturer name (e.g. "Bambu Lab")
    material : Material / finish type ("PLA", "PETG", "ABS", "TPU",
               "Silk", "Matte" or "Wood")
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
    {"brand": "Hatchbox", "material": "PLA", "name": "White", "hex": "#F7F7F4", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Black", "hex": "#1A1A1A", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "True Red", "hex": "#B01B22", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Blue", "hex": "#1F4E9B", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Green", "hex": "#2E8B57", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Yellow", "hex": "#F2C50B", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Orange", "hex": "#E8641A", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Purple", "hex": "#6A3FA0", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PLA", "name": "Gray", "hex": "#7D7F7C", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Black", "hex": "#151515", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG White", "hex": "#FAFAFA", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Red", "hex": "#A5202A", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "PETG", "name": "PETG Blue", "hex": "#22548F", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS Black", "hex": "#181818", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS White", "hex": "#F4F4F0", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},
    {"brand": "Hatchbox", "material": "ABS", "name": "ABS Red", "hex": "#AE1C24", "url": "https://www.amazon.com/stores/HATCHBOX/page/BE84484A-154A-49EC-BF3F-FF4CE6E4ECB7"},

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
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Cotton White", "hex": "#F2EFE9", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Charcoal Black", "hex": "#26262A", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Army Red", "hex": "#9E2B25", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Sapphire Blue", "hex": "#1D4E89", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Forest Green", "hex": "#2C6E49", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyLite Yellow", "hex": "#F4C20D", "url": "https://shop.polymaker.com/products/polylite-pla"},
    {"brand": "Polymaker", "material": "PLA", "name": "PolyTerra Muted Grey", "hex": "#8A8D8F", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG Black", "hex": "#161616", "url": "https://shop.polymaker.com/products/polymaker-petg"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG White", "hex": "#F7F7F3", "url": "https://shop.polymaker.com/products/polymaker-petg"},
    {"brand": "Polymaker", "material": "PETG", "name": "PolyLite PETG Teal", "hex": "#008C99", "url": "https://shop.polymaker.com/products/polymaker-petg"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS Black", "hex": "#131313", "url": "https://shop.polymaker.com/products/polylite-abs"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS White", "hex": "#F4F4EF", "url": "https://shop.polymaker.com/products/polylite-abs"},
    {"brand": "Polymaker", "material": "ABS", "name": "PolyLite ABS Orange", "hex": "#EC6B1F", "url": "https://shop.polymaker.com/products/polylite-abs"},

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

    # ------------------------------------------------------------------ #
    # Additional Bambu Lab colors (for 8 / 16-color AMS palettes)        #
    # ------------------------------------------------------------------ #
    {"brand": "Bambu Lab", "material": "PLA", "name": "Beige", "hex": "#D3C5A2", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Cocoa Brown", "hex": "#6F5034", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Turquoise", "hex": "#00B1B7", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Bright Green", "hex": "#BECF00", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Maroon Red", "hex": "#9D2235", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Indigo Purple", "hex": "#482960", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Light Gray", "hex": "#D1D3D5", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},
    {"brand": "Bambu Lab", "material": "PLA", "name": "Dark Gray", "hex": "#545454", "url": "https://us.store.bambulab.com/products/pla-basic-filament"},

    # ------------------------------------------------------------------ #
    # ColorFabb (premium)                                                #
    # ------------------------------------------------------------------ #
    {"brand": "ColorFabb", "material": "PLA", "name": "Traffic White", "hex": "#F4F5F0", "url": "https://colorfabb.com/pla-pha"},
    {"brand": "ColorFabb", "material": "PLA", "name": "Intense Black", "hex": "#0F0F10", "url": "https://colorfabb.com/pla-pha"},
    {"brand": "ColorFabb", "material": "PLA", "name": "Red", "hex": "#B5202A", "url": "https://colorfabb.com/pla-pha"},
    {"brand": "ColorFabb", "material": "PLA", "name": "Ultramarine Blue", "hex": "#123C8C", "url": "https://colorfabb.com/pla-pha"},
    {"brand": "ColorFabb", "material": "PLA", "name": "Leaf Green", "hex": "#3F8A3B", "url": "https://colorfabb.com/pla-pha"},
    {"brand": "ColorFabb", "material": "PETG", "name": "PETG White", "hex": "#F6F6F1", "url": "https://colorfabb.com/petg-economy"},
    {"brand": "ColorFabb", "material": "PETG", "name": "PETG Black", "hex": "#131316", "url": "https://colorfabb.com/petg-economy"},

    # ------------------------------------------------------------------ #
    # MatterHackers (Build & PRO series)                                 #
    # ------------------------------------------------------------------ #
    {"brand": "MatterHackers", "material": "PLA", "name": "White", "hex": "#F7F7F4", "url": "https://www.matterhackers.com/store/c/build-series-pla"},
    {"brand": "MatterHackers", "material": "PLA", "name": "Black", "hex": "#141414", "url": "https://www.matterhackers.com/store/c/build-series-pla"},
    {"brand": "MatterHackers", "material": "PLA", "name": "Red", "hex": "#C31F2C", "url": "https://www.matterhackers.com/store/c/build-series-pla"},
    {"brand": "MatterHackers", "material": "PLA", "name": "Blue", "hex": "#1E5AA8", "url": "https://www.matterhackers.com/store/c/build-series-pla"},
    {"brand": "MatterHackers", "material": "PLA", "name": "Green", "hex": "#2E9E44", "url": "https://www.matterhackers.com/store/c/build-series-pla"},
    {"brand": "MatterHackers", "material": "PETG", "name": "PETG Black", "hex": "#151517", "url": "https://www.matterhackers.com/store/c/pro-series-petg"},
    {"brand": "MatterHackers", "material": "ABS", "name": "ABS White", "hex": "#F3F3EE", "url": "https://www.matterhackers.com/store/c/pro-series-abs"},

    # ------------------------------------------------------------------ #
    # Atomic Filament                                                    #
    # ------------------------------------------------------------------ #
    {"brand": "Atomic Filament", "material": "PLA", "name": "Max White", "hex": "#FBFBF8", "url": "https://atomicfilament.com/"},
    {"brand": "Atomic Filament", "material": "PLA", "name": "Midnight Black", "hex": "#0C0C0E", "url": "https://atomicfilament.com/"},
    {"brand": "Atomic Filament", "material": "PLA", "name": "Fire Red", "hex": "#C51726", "url": "https://atomicfilament.com/"},
    {"brand": "Atomic Filament", "material": "PETG", "name": "PETG Black", "hex": "#131315", "url": "https://atomicfilament.com/collections/petg-3d-printer-filament-us-made-with-free-shipping"},

    # ------------------------------------------------------------------ #
    # IC3D                                                               #
    # ------------------------------------------------------------------ #
    {"brand": "IC3D", "material": "PLA", "name": "White", "hex": "#F5F5F1", "url": "https://www.ic3dprinters.com/collections/pla"},
    {"brand": "IC3D", "material": "PLA", "name": "Black", "hex": "#161616", "url": "https://www.ic3dprinters.com/collections/pla"},
    {"brand": "IC3D", "material": "ABS", "name": "ABS Black", "hex": "#161618", "url": "https://www.ic3dprinters.com/collections/abs"},

    # ------------------------------------------------------------------ #
    # Amazon Basics (budget)                                             #
    # ------------------------------------------------------------------ #
    {"brand": "Amazon Basics", "material": "PLA", "name": "White", "hex": "#F6F6F2", "url": "https://www.amazon.com/s?k=3d+printer+filament+pla"},
    {"brand": "Amazon Basics", "material": "PLA", "name": "Black", "hex": "#171717", "url": "https://www.amazon.com/s?k=3d+printer+filament+pla"},
    {"brand": "Amazon Basics", "material": "PLA", "name": "Red", "hex": "#BE212C", "url": "https://www.amazon.com/s?k=3d+printer+filament+pla"},
    {"brand": "Amazon Basics", "material": "PLA", "name": "Blue", "hex": "#20599E", "url": "https://www.amazon.com/s?k=3d+printer+filament+pla"},

    # ------------------------------------------------------------------ #
    # Inland (Micro Center)                                              #
    # ------------------------------------------------------------------ #
    {"brand": "Inland", "material": "PLA", "name": "White", "hex": "#F7F7F3", "url": "https://www.microcenter.com/site/content/inland%20filament.aspx"},
    {"brand": "Inland", "material": "PLA", "name": "Black", "hex": "#151515", "url": "https://www.microcenter.com/site/content/inland%20filament.aspx"},
    {"brand": "Inland", "material": "PLA", "name": "Red", "hex": "#C11F2A", "url": "https://www.microcenter.com/site/content/inland%20filament.aspx"},
    {"brand": "Inland", "material": "PETG", "name": "PETG Black", "hex": "#141416", "url": "https://www.microcenter.com/site/content/inland%20filament.aspx"},

    # ------------------------------------------------------------------ #
    # Elegoo                                                             #
    # ------------------------------------------------------------------ #
    {"brand": "Elegoo", "material": "PLA", "name": "White", "hex": "#F6F6F3", "url": "https://www.elegoo.com/collections/pla-filament"},
    {"brand": "Elegoo", "material": "PLA", "name": "Black", "hex": "#141414", "url": "https://www.elegoo.com/collections/pla-filament"},
    {"brand": "Elegoo", "material": "PLA", "name": "Red", "hex": "#C21E2A", "url": "https://www.elegoo.com/collections/pla-filament"},
    {"brand": "Elegoo", "material": "PLA", "name": "Grey", "hex": "#7C7F82", "url": "https://www.elegoo.com/collections/pla-filament"},

    # ------------------------------------------------------------------ #
    # Creality (Hyper series)                                            #
    # ------------------------------------------------------------------ #
    {"brand": "Creality", "material": "PLA", "name": "White", "hex": "#F7F7F4", "url": "https://store.creality.com/collections/filament"},
    {"brand": "Creality", "material": "PLA", "name": "Black", "hex": "#151515", "url": "https://store.creality.com/collections/filament"},
    {"brand": "Creality", "material": "PLA", "name": "Red", "hex": "#C41F2B", "url": "https://store.creality.com/collections/filament"},
    {"brand": "Creality", "material": "PLA", "name": "Blue", "hex": "#1F59A4", "url": "https://store.creality.com/collections/filament"},

    # ------------------------------------------------------------------ #
    # 3D Solutech                                                        #
    # ------------------------------------------------------------------ #
    {"brand": "3D Solutech", "material": "PLA", "name": "Natural Clear", "hex": "#EDEDE4", "url": "https://www.amazon.com/s?k=3d+solutech+pla+filament"},
    {"brand": "3D Solutech", "material": "PLA", "name": "Real Black", "hex": "#131313", "url": "https://www.amazon.com/s?k=3d+solutech+pla+filament"},
    {"brand": "3D Solutech", "material": "PLA", "name": "Apple Green", "hex": "#4FA83D", "url": "https://www.amazon.com/s?k=3d+solutech+pla+filament"},

    # ================================================================== #
    # MATTE PLA — flat, non-reflective finish (great for models/figures) #
    # ================================================================== #
    # ---- Bambu Lab PLA Matte ---- #
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Ivory White", "hex": "#EDE9DE", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Bone White", "hex": "#E4DCC8", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Charcoal", "hex": "#26282B", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Ash Grey", "hex": "#9B9EA0", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Nardo Grey", "hex": "#6C6E6C", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Scarlet Red", "hex": "#C3272B", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Dark Red", "hex": "#88191B", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Mandarin Orange", "hex": "#E8631A", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Lemon Yellow", "hex": "#F5C518", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Grass Green", "hex": "#5E9A3E", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Dark Green", "hex": "#2C5A3A", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Ice Blue", "hex": "#A7C7DA", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Marine Blue", "hex": "#1F5C8B", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Sakura Pink", "hex": "#F3B9C4", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Lilac Purple", "hex": "#8A7CB6", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Latte Brown", "hex": "#9A6B45", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Desert Tan", "hex": "#C7A97B", "url": "https://us.store.bambulab.com/products/pla-matte"},
    {"brand": "Bambu Lab", "material": "Matte", "name": "Matte Terracotta", "hex": "#B4553A", "url": "https://us.store.bambulab.com/products/pla-matte"},
    # ---- Polymaker PolyTerra Matte PLA ---- #
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Cotton White", "hex": "#ECE9E1", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Charcoal Black", "hex": "#292A2D", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Lava Red", "hex": "#B32C2C", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Sunrise Orange", "hex": "#E96B26", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Sapphire Blue", "hex": "#20509A", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Forest Green", "hex": "#2F6B49", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Muted Yellow", "hex": "#E6C23A", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    {"brand": "Polymaker", "material": "Matte", "name": "PolyTerra Fossil Grey", "hex": "#8C8D88", "url": "https://shop.polymaker.com/products/polyterra-pla"},
    # ---- Overture Matte PLA ---- #
    {"brand": "Overture", "material": "Matte", "name": "Matte White", "hex": "#EEEBE3", "url": "https://overture3d.com/collections/matte-pla"},
    {"brand": "Overture", "material": "Matte", "name": "Matte Black", "hex": "#242424", "url": "https://overture3d.com/collections/matte-pla"},
    {"brand": "Overture", "material": "Matte", "name": "Matte Red", "hex": "#BE2F2F", "url": "https://overture3d.com/collections/matte-pla"},
    {"brand": "Overture", "material": "Matte", "name": "Matte Blue", "hex": "#28598F", "url": "https://overture3d.com/collections/matte-pla"},
    {"brand": "Overture", "material": "Matte", "name": "Matte Green", "hex": "#3B7A4A", "url": "https://overture3d.com/collections/matte-pla"},

    # ================================================================== #
    # SILK PLA — glossy, metallic sheen                                  #
    # ================================================================== #
    # ---- Bambu Lab PLA Silk / Silk+ ---- #
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Gold", "hex": "#D4A73B", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Silver", "hex": "#B9BCBE", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Champagne", "hex": "#C9B98E", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Blue", "hex": "#2E6FC4", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Purple", "hex": "#7A4FC0", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Pink", "hex": "#EC7CA8", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Candy Green", "hex": "#2FA86A", "url": "https://us.store.bambulab.com/products/pla-silk"},
    {"brand": "Bambu Lab", "material": "Silk", "name": "Silk Candy Red", "hex": "#CE2C43", "url": "https://us.store.bambulab.com/products/pla-silk"},
    # ---- SUNLU Silk PLA ---- #
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Gold", "hex": "#CBA135", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Silver", "hex": "#BEC1C3", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Copper", "hex": "#B4633A", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Red", "hex": "#CC2733", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Blue", "hex": "#2C74C0", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    {"brand": "SUNLU", "material": "Silk", "name": "Silk Rainbow", "hex": "#9B6FB0", "url": "https://www.sunlu.com/collections/silk-pla-filament"},
    # ---- eSun eSilk PLA ---- #
    {"brand": "eSun", "material": "Silk", "name": "eSilk Gold", "hex": "#CFA53C", "url": "https://www.esun3d.com/esilk-pla-product/"},
    {"brand": "eSun", "material": "Silk", "name": "eSilk Silver", "hex": "#BCC0C2", "url": "https://www.esun3d.com/esilk-pla-product/"},
    {"brand": "eSun", "material": "Silk", "name": "eSilk Bronze", "hex": "#A9793F", "url": "https://www.esun3d.com/esilk-pla-product/"},
    {"brand": "eSun", "material": "Silk", "name": "eSilk Pink", "hex": "#E884A6", "url": "https://www.esun3d.com/esilk-pla-product/"},

    # ================================================================== #
    # TPU — flexible filament                                            #
    # ================================================================== #
    # ---- Bambu Lab TPU for AMS (95A) ---- #
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU Black", "hex": "#1B1B1B", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU White", "hex": "#F1F1EC", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU Red", "hex": "#C1272D", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU Blue", "hex": "#1F5FA8", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU Neon Green", "hex": "#7ED957", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    {"brand": "Bambu Lab", "material": "TPU", "name": "TPU Yellow", "hex": "#F4C022", "url": "https://us.store.bambulab.com/products/tpu-for-ams"},
    # ---- eSun eTPU-95A ---- #
    {"brand": "eSun", "material": "TPU", "name": "eTPU Black", "hex": "#161616", "url": "https://www.esun3d.com/etpu-95a-product/"},
    {"brand": "eSun", "material": "TPU", "name": "eTPU White", "hex": "#F5F5F0", "url": "https://www.esun3d.com/etpu-95a-product/"},
    {"brand": "eSun", "material": "TPU", "name": "eTPU Red", "hex": "#C0202B", "url": "https://www.esun3d.com/etpu-95a-product/"},
    {"brand": "eSun", "material": "TPU", "name": "eTPU Blue", "hex": "#1E5DA8", "url": "https://www.esun3d.com/etpu-95a-product/"},
    {"brand": "eSun", "material": "TPU", "name": "eTPU Orange", "hex": "#EE6A1D", "url": "https://www.esun3d.com/etpu-95a-product/"},
    {"brand": "eSun", "material": "TPU", "name": "eTPU Grey", "hex": "#808285", "url": "https://www.esun3d.com/etpu-95a-product/"},
    # ---- Polymaker PolyFlex TPU95 ---- #
    {"brand": "Polymaker", "material": "TPU", "name": "PolyFlex Black", "hex": "#141414", "url": "https://shop.polymaker.com/products/polyflex-tpu95"},
    {"brand": "Polymaker", "material": "TPU", "name": "PolyFlex White", "hex": "#F4F4EF", "url": "https://shop.polymaker.com/products/polyflex-tpu95"},
    {"brand": "Polymaker", "material": "TPU", "name": "PolyFlex Red", "hex": "#BE222E", "url": "https://shop.polymaker.com/products/polyflex-tpu95"},
    {"brand": "Polymaker", "material": "TPU", "name": "PolyFlex Blue", "hex": "#215BA0", "url": "https://shop.polymaker.com/products/polyflex-tpu95"},
    # ---- SainSmart / SUNLU flexible ---- #
    {"brand": "SUNLU", "material": "TPU", "name": "TPU Black", "hex": "#151515", "url": "https://www.sunlu.com/collections/tpu-filament"},
    {"brand": "SUNLU", "material": "TPU", "name": "TPU Transparent", "hex": "#E9E9E2", "url": "https://www.sunlu.com/collections/tpu-filament"},
    {"brand": "SUNLU", "material": "TPU", "name": "TPU Red", "hex": "#C31C28", "url": "https://www.sunlu.com/collections/tpu-filament"},

    # ================================================================== #
    # WOOD-FILLED PLA — matte, wood-tone finish                          #
    # ================================================================== #
    # ---- Bambu Lab PLA Wood ---- #
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood Clay Brown", "hex": "#8B5A2B", "url": "https://us.store.bambulab.com/products/pla-wood"},
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood Rosewood", "hex": "#6E3B2E", "url": "https://us.store.bambulab.com/products/pla-wood"},
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood Classic Birch", "hex": "#C7A876", "url": "https://us.store.bambulab.com/products/pla-wood"},
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood Black Walnut", "hex": "#4A342A", "url": "https://us.store.bambulab.com/products/pla-wood"},
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood White Oak", "hex": "#B99C74", "url": "https://us.store.bambulab.com/products/pla-wood"},
    {"brand": "Bambu Lab", "material": "Wood", "name": "Wood Ochre Yellow", "hex": "#B98A34", "url": "https://us.store.bambulab.com/products/pla-wood"},
    # ---- ColorFabb woodFill ---- #
    {"brand": "ColorFabb", "material": "Wood", "name": "woodFill", "hex": "#9C6B3F", "url": "https://colorfabb.com/woodfill"},
    {"brand": "ColorFabb", "material": "Wood", "name": "bambooFill", "hex": "#C0A067", "url": "https://colorfabb.com/bamboofill"},
    {"brand": "ColorFabb", "material": "Wood", "name": "corkFill", "hex": "#A9805A", "url": "https://colorfabb.com/corkfill"},
    # ---- Polymaker PolyWood / SUNLU Wood ---- #
    {"brand": "Polymaker", "material": "Wood", "name": "PolyWood Natural", "hex": "#B58A55", "url": "https://shop.polymaker.com/products/polywood"},
    {"brand": "SUNLU", "material": "Wood", "name": "Wood Natural", "hex": "#A9773F", "url": "https://www.sunlu.com/collections/wood-pla-filament"},
    {"brand": "SUNLU", "material": "Wood", "name": "Wood Dark", "hex": "#5E4126", "url": "https://www.sunlu.com/collections/wood-pla-filament"},
]


# ---------------------------------------------------------------------------
# Approximate retail pricing (USD per 1 kg spool) used by the cost calculator.
# Prices are rough street prices and can be edited to match what you actually
# pay. Looked up by (brand, material) with a material-level fallback.
# ---------------------------------------------------------------------------
_PRICE_PER_KG: Dict[str, float] = {
    "Bambu Lab|PLA": 19.99, "Bambu Lab|PETG": 24.99, "Bambu Lab|ABS": 24.99,
    "Hatchbox|PLA": 22.99, "Hatchbox|PETG": 24.99, "Hatchbox|ABS": 23.99,
    "Prusament|PLA": 29.99, "Prusament|PETG": 29.99, "Prusament|ABS": 29.99,
    "eSun|PLA": 18.99, "eSun|PETG": 20.99, "eSun|ABS": 19.99,
    "Polymaker|PLA": 21.99, "Polymaker|PETG": 24.99, "Polymaker|ABS": 23.99,
    "Overture|PLA": 18.99, "Overture|PETG": 20.99,
    "SUNLU|PLA": 15.99, "SUNLU|PETG": 17.99,
    "ColorFabb|PLA": 34.99, "ColorFabb|PETG": 36.99,
    "MatterHackers|PLA": 22.99, "MatterHackers|PETG": 27.99, "MatterHackers|ABS": 25.99,
    "Atomic Filament|PLA": 27.99, "Atomic Filament|PETG": 29.99,
    "IC3D|PLA": 23.99, "IC3D|ABS": 24.99,
    "Amazon Basics|PLA": 17.99,
    "Inland|PLA": 14.99, "Inland|PETG": 16.99,
    "Elegoo|PLA": 13.99,
    "Creality|PLA": 17.99,
    "3D Solutech|PLA": 19.99,

    # Matte PLA
    "Bambu Lab|Matte": 19.99, "Polymaker|Matte": 21.99, "Overture|Matte": 19.99,
    # Silk PLA
    "Bambu Lab|Silk": 24.99, "SUNLU|Silk": 18.99, "eSun|Silk": 21.99,
    # TPU (flexible)
    "Bambu Lab|TPU": 34.99, "eSun|TPU": 27.99, "Polymaker|TPU": 32.99, "SUNLU|TPU": 22.99,
    # Wood-filled PLA
    "Bambu Lab|Wood": 24.99, "ColorFabb|Wood": 44.99, "Polymaker|Wood": 29.99, "SUNLU|Wood": 21.99,
}

# Material-level fallback prices (USD/kg) when a specific brand isn't listed.
_MATERIAL_FALLBACK_PRICE: Dict[str, float] = {
    "PLA": 20.0, "PETG": 23.0, "ABS": 23.0,
    "Matte": 21.0, "Silk": 22.0, "TPU": 30.0, "Wood": 28.0,
}


def _hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Convert a ``#RRGGBB`` string to an ``(r, g, b)`` int tuple."""
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i + 2], 16) for i in (0, 2, 4))


def get_price_per_kg(brand: str, material: str) -> float:
    """
    Return the approximate price (USD per 1 kg spool) for a brand/material.

    Falls back to a material-level average when the exact brand isn't listed,
    and finally to a generic default.
    """
    key = f"{brand}|{material}"
    if key in _PRICE_PER_KG:
        return _PRICE_PER_KG[key]
    return _MATERIAL_FALLBACK_PRICE.get(material, 20.0)


def get_filaments() -> List[Dict]:
    """Return the full filament list with added ``rgb`` and ``price_per_kg`` values."""
    filaments = []
    for entry in _FILAMENTS:
        item = dict(entry)
        item["rgb"] = _hex_to_rgb(entry["hex"])
        item["price_per_kg"] = get_price_per_kg(entry["brand"], entry["material"])
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
