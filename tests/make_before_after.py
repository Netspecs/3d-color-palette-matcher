"""Generate docs/v2_1_before_after.png - OLD vs NEW palette on the Seahawks photo."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont

import color_utils as cu
import filament_database as fdb
from test_v2_1_seahawks import old_palette, new_palette, PHOTO

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "docs", "v2_1_before_after.png")

BG = (24, 26, 32)
CARD = (36, 39, 48)
FG = (235, 237, 242)
SUB = (150, 155, 165)
ACCENT = (90, 170, 120)
WARN = (210, 120, 110)


def _font(sz, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def _match(rgb):
    return cu.match_filaments(rgb, fdb.get_filaments(), top_n=1)[0]


def _ideal_text(rgb):
    return (20, 20, 20) if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) > 140 else FG


def draw_palette(draw, x, y, w, title, subtitle, colors, title_color):
    f_title = _font(26, True)
    f_sub = _font(15)
    f_row = _font(15, True)
    f_small = _font(13)
    draw.text((x, y), title, font=f_title, fill=title_color)
    draw.text((x, y + 34), subtitle, font=f_sub, fill=SUB)
    ry = y + 68
    row_h = 54
    for c in colors:
        rgb = c["rgb"]
        pct = c["percentage"]
        m = _match(rgb)
        draw.rounded_rectangle([x, ry, x + w, ry + row_h - 8], radius=8, fill=CARD)
        # swatch
        sw = 42
        draw.rounded_rectangle([x + 8, ry + 2, x + 8 + sw, ry + 2 + sw], radius=6,
                               fill=rgb, outline=(70, 74, 84))
        hexs = "#%02X%02X%02X" % rgb
        tx = x + 8 + sw + 12
        draw.text((tx, ry + 4), f"{hexs}   {pct:.0f}%", font=f_row, fill=FG)
        draw.text((tx, ry + 25), f"-> {m['brand']} {m['name']} ({m['material']}) dE {m['distance']:.1f}",
                  font=f_small, fill=SUB)
        ry += row_h
    return ry


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    old = old_palette(4)
    _, _, new_all = new_palette(10)
    # show the real print colours: top by share, but guarantee the action
    # green is visible (it is a small but important share of the print).
    new = new_all[:6]
    if not any(c["rgb"][1] > c["rgb"][0] + 20 and c["rgb"][1] > c["rgb"][2] + 10 for c in new):
        green = next((c for c in new_all if c["rgb"][1] > c["rgb"][0] + 20
                      and c["rgb"][1] > c["rgb"][2] + 10), None)
        if green:
            new = new + [green]

    W, H = 1180, 760
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.text((40, 28), "3D Print Color Palette Matcher v2.1", font=_font(30, True), fill=FG)
    draw.text((40, 68), "Seahawks print on a bronze Bambu build plate - fixing the \"false colors\" bug",
              font=_font(16), fill=SUB)

    # source photo thumbnail
    photo = Image.open(PHOTO).convert("RGB")
    pw = 300
    ph = int(photo.height * pw / photo.width)
    photo.thumbnail((pw, ph))
    px, py = 40, 110
    draw.rounded_rectangle([px - 6, py - 6, px + photo.width + 6, py + photo.height + 6],
                           radius=10, fill=CARD)
    img.paste(photo, (px, py))
    draw.text((px, py + photo.height + 10), "Source photo", font=_font(13), fill=SUB)

    col_y = 110
    draw_palette(draw, 380, col_y, 360,
                 "BEFORE (v2.0)",
                 "Whole image - plate dominates (81% brown)",
                 old, WARN)
    draw_palette(draw, 780, col_y, 360,
                 "AFTER (v2.1)",
                 "Bronze plate click-removed (0% brown)",
                 new, ACCENT)

    foot = ("v2.1: Lab clustering with CIEDE2000 merge + background removal (auto / click-remove / "
            "crop / mask preview). Real print colors - navy, white, gray, green - now recovered.")
    draw.text((40, H - 34), foot, font=_font(13), fill=SUB)

    img.save(OUT)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()
