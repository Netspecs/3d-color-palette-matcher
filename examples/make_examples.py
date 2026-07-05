"""
Generate a handful of sample images you can drop into the app to try it out.

Run:  python examples/make_examples.py
Creates several PNGs in the same folder.
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))


def _save(img, name):
    path = os.path.join(HERE, name)
    img.save(path)
    print("wrote", path)


def sunset():
    """Warm vertical gradient with a sun disc — 3-4 dominant colors."""
    w, h = 480, 320
    img = Image.new("RGB", (w, h))
    px = img.load()
    top = (28, 30, 82)       # deep indigo
    bottom = (255, 138, 42)  # orange
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    # sun
    cx, cy, rad = w * 0.5, h * 0.62, 55
    for y in range(h):
        for x in range(w):
            if (x - cx) ** 2 + (y - cy) ** 2 <= rad ** 2:
                px[x, y] = (255, 221, 120)
    _save(img, "sunset.png")


def blocks():
    """Four solid quadrants — clean 4-color test (great for AMS)."""
    w, h = 400, 400
    img = Image.new("RGB", (w, h))
    px = img.load()
    quad = [(198, 40, 45), (30, 100, 170), (46, 160, 70), (245, 200, 40)]
    for y in range(h):
        for x in range(w):
            px[x, y] = quad[(x // (w // 2)) + 2 * (y // (h // 2))]
    _save(img, "four_blocks.png")


def rainbow():
    """Horizontal hue sweep — good for testing 8/16-color palettes."""
    import colorsys
    w, h = 512, 200
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        r, g, b = colorsys.hsv_to_rgb(x / w, 0.85, 0.95)
        col = (int(r * 255), int(g * 255), int(b * 255))
        for y in range(h):
            px[x, y] = col
    _save(img, "rainbow.png")


def waves():
    """Soft teal/navy waves — muted palette for realistic matching."""
    w, h = 480, 300
    img = Image.new("RGB", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(w):
            v = (math.sin(x / 40.0) + math.sin(y / 30.0)) * 0.5
            t = (v + 1) / 2
            r = int(18 + 40 * t)
            g = int(70 + 120 * t)
            b = int(90 + 110 * t)
            px[x, y] = (r, g, b)
    _save(img, "waves.png")


if __name__ == "__main__":
    sunset()
    blocks()
    rainbow()
    waves()
    print("Done. Drop any of these into the app to try it out.")
