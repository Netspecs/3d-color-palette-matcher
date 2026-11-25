"""
v2.1 extraction test on the real Seahawks photo.

Proves the "false colors" bug is fixed: the OLD pipeline returns the brown
build-plate colors; the NEW pipeline (with the bronze plate click-removed)
surfaces the real print colors - navy, white, gray/silver and green - and
NOT the brown plate.

Run: python3 tests/test_v2_1_seahawks.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

import color_utils as cu
import filament_database as fdb

PHOTO = "/home/ubuntu/Uploads/Screenshot 2026-11-25 011431.png"
# Clean bronze build-plate sample points (normalised x, y) - the empty plate
# area below the logo, both light and darker bronze patches.
PLATE_POINTS = [
    (0.50, 0.55), (0.38, 0.60), (0.62, 0.58),
    (0.50, 0.68), (0.30, 0.52), (0.70, 0.52),
]
PLATE_TOL = 24.0


def _match(rgb):
    return cu.match_filaments(rgb, fdb.get_filaments(), top_n=1)[0]


def old_palette(n=4):
    return cu.extract_colors(PHOTO, n)


def new_palette(n=10):
    arr = cu.load_rgb_array(PHOTO)
    h, w, _ = arr.shape
    excl = [
        {"rgb": tuple(int(v) for v in arr[int(y * (h - 1)), int(x * (w - 1))]),
         "tol": PLATE_TOL}
        for x, y in PLATE_POINTS
    ]
    mask = cu.compute_keep_mask(arr, exclusions=excl)
    return arr, mask, cu.extract_colors_from_pixels(arr[mask], num_colors=n)


def _is_navy(rgb):
    r, g, b = rgb
    return (b - r) > 12 and 35 < b < 130


def _is_green(rgb):
    r, g, b = rgb
    return g > r + 20 and g > b + 10


def _is_light_neutral(rgb):
    r, g, b = rgb
    return min(rgb) > 150 and (max(rgb) - min(rgb)) < 45


def _is_brown(rgb):
    r, g, b = rgb
    return r > g > b and (r - b) > 25 and 50 < r < 200


def main():
    print("=== OLD pipeline (whole image, 4 colors) ===")
    old = old_palette(4)
    for c in old:
        m = _match(c["rgb"])
        print(f"  {c['rgb']}  {c['percentage']:5.1f}%  -> {m['brand']} {m['name']} "
              f"{m['material']} (dE={m['distance']:.2f})")

    _, mask, new = new_palette(10)
    print(f"\n=== NEW pipeline (bronze plate click-removed, kept {mask.mean()*100:.0f}%) ===")
    for c in new:
        m = _match(c["rgb"])
        print(f"  {c['rgb']}  {c['percentage']:5.1f}%  -> {m['brand']} {m['name']} "
              f"{m['material']} (dE={m['distance']:.2f})")

    new_rgbs = [c["rgb"] for c in new]
    has_navy = any(_is_navy(c) for c in new_rgbs)
    has_green = any(_is_green(c) for c in new_rgbs)
    has_light = any(_is_light_neutral(c) for c in new_rgbs)
    # brown should no longer DOMINATE (not the top colour, small share)
    brown_share = sum(c["percentage"] for c in new if _is_brown(c["rgb"]))
    old_brown_share = sum(c["percentage"] for c in old if _is_brown(c["rgb"]))

    print("\n=== Assertions ===")
    print(f"  NEW has navy:         {has_navy}")
    print(f"  NEW has green:        {has_green}")
    print(f"  NEW has light neutral:{has_light}")
    print(f"  OLD brown share:      {old_brown_share:.0f}%")
    print(f"  NEW brown share:      {brown_share:.0f}%")

    assert has_navy, "NEW palette missing navy"
    assert has_green, "NEW palette missing green"
    assert has_light, "NEW palette missing white/light gray"
    assert old_brown_share > 50, "OLD palette should be brown-dominated"
    assert brown_share < 20, "NEW palette should not be brown-dominated"
    print("\nALL ASSERTIONS PASSED")


if __name__ == "__main__":
    main()
