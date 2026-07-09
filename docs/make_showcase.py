"""Compose a v2.0 showcase collage from the captured window screenshots."""
from PIL import Image, ImageDraw, ImageFont

BG = (17, 18, 26)
CARD = (30, 32, 44)
FG = (233, 235, 244)
MUT = (150, 155, 170)
ACCENT = (52, 199, 138)

def font(sz, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()

def load(name):
    return Image.open(name).convert("RGB")

main = load("v2_main.png")
planner = load("v2_planner.png")
preview = load("v2_preview.png")
enter = load("v2_entercolors.png")

W = 1240
PAD = 24
# Layout: title, big main, then a row of 3 smaller (planner, preview, enter)
title_h = 96
main_w = W - 2 * PAD
scale = main_w / main.width
main_r = main.resize((main_w, int(main.height * scale)))

small_w = (W - 4 * PAD) // 3
def fit(img, w):
    s = w / img.width
    return img.resize((w, int(img.height * s)))

pl = fit(planner, small_w)
pv = fit(preview, small_w)
en = fit(enter, small_w)
row_h = max(pl.height, pv.height, en.height)

H = title_h + PAD + main_r.height + PAD + 34 + row_h + PAD
canvas = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(canvas)

# Title
d.text((PAD, 24), "3D Print Color Palette Matcher", font=font(34, True), fill=FG)
d.text((PAD, 64), "v2.0  ·  CIEDE2000 matching · print planner · filament preview · 225 filaments · direct color input",
        font=font(15), fill=ACCENT)

y = title_h
canvas.paste(main_r, (PAD, y))
y += main_r.height + PAD

d.text((PAD, y), "Print planner (AMS/MMU3/IDEX)     ·     Filament preview     ·     Direct hex input",
        font=font(15, True), fill=MUT)
y += 30
canvas.paste(pl, (PAD, y))
canvas.paste(pv, (PAD * 2 + small_w, y))
canvas.paste(en, (PAD * 3 + small_w * 2, y))

canvas.save("v2_showcase.png")
print("saved v2_showcase.png", canvas.size)
