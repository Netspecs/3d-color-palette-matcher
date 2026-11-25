"""Headless Tkinter UI screenshots for v2.1 (mask preview + results).

Runs under Xvfb (DISPLAY=:1) with drag-and-drop disabled, loads the Seahawks
photo, click-removes the bronze plate, captures the mask preview, then runs
matching and captures the results.  Uses `import -window root` (ImageMagick).
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force DnD off BEFORE importing app so it never touches the native tkdnd lib.
import app as appmod
appmod._DND_AVAILABLE = False

import color_utils as cu

PHOTO = "/home/ubuntu/Uploads/Screenshot 2026-11-25 011431.png"
DOCS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
PLATE_POINTS = [(0.50, 0.55), (0.38, 0.60), (0.62, 0.58),
                (0.50, 0.68), (0.30, 0.52), (0.70, 0.52)]


def pump(root, n=12):
    for _ in range(n):
        root.update_idletasks()
        root.update()
        time.sleep(0.03)


def grab(path):
    subprocess.run(["import", "-window", "root", path], check=True,
                   env={**os.environ, "DISPLAY": ":1"})
    print("saved", path)


def main():
    from tkinter import Tk
    root = Tk()
    root.geometry("1024x720+0+0")
    a = appmod.ColorMatcherApp(root)
    pump(root)

    # Load the photo into the working image + canvas.
    a.load_image(PHOTO)
    pump(root)

    # Simulate click-remove on the bronze plate (6 sample points) + tolerance.
    a.mask_tol.set(24)
    h, w, _ = a.work_arr.shape
    for xn, yn in PLATE_POINTS:
        rgb = tuple(int(v) for v in a.work_arr[int(yn * (h - 1)), int(xn * (w - 1))])
        if rgb not in a.excluded_colors:
            a.excluded_colors.append(rgb)
    a._set_mode("remove")
    a._update_canvas()
    a.status.set("Bronze plate removed (6 colors). Checkerboard = removed. Click Match Colors.")
    pump(root)
    grab(os.path.join(DOCS, "v2_1_mask_preview.png"))

    # Run matching synchronously and capture results.
    a.num_colors.set(10)
    a._do_matching()          # fills a.results, schedules _display_results
    pump(root, 20)            # let root.after(0, ...) fire
    grab(os.path.join(DOCS, "v2_1_results.png"))

    root.destroy()
    print("done")


if __name__ == "__main__":
    main()
