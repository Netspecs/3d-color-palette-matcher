"""
3D Print Color Palette Matcher
==============================

A desktop application that extracts the dominant colors from an image and
matches them to real-world 3D printing filament colors from popular brands
(Bambu Lab, Hatchbox, Prusament, eSun, Polymaker, and more), covering PLA,
ABS and PETG.

Ideal for planning multi-color prints on Bambu Lab AMS (4 / 8 / 16 color),
Snapmaker and other multi-material systems.

Run with:  python app.py
"""

import json
import os
import threading
import webbrowser
from tkinter import (
    Tk, Frame, Label, Button, Canvas, StringVar, IntVar, OptionMenu,
    Scale, HORIZONTAL, filedialog, messagebox, Scrollbar, LEFT, RIGHT, BOTH,
    X, Y, TOP, W, E, VERTICAL, END,
)
from tkinter import ttk

from PIL import Image, ImageTk

import color_utils as cu
import filament_database as fdb

# Optional drag-and-drop support (graceful fallback if not installed)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    _DND_AVAILABLE = False


# ---------------------------------------------------------------------------
# Theme / styling constants
# ---------------------------------------------------------------------------
BG = "#1e1f26"
BG_PANEL = "#282a36"
BG_CARD = "#33354a"
FG = "#f8f8f2"
FG_MUTED = "#a9abbd"
ACCENT = "#50b98a"
ACCENT_DARK = "#3c8f69"
FONT = "Segoe UI"

SUPPORTED_TYPES = [
    ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
    ("All files", "*.*"),
]


class ColorMatcherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Print Color Palette Matcher")
        self.root.geometry("1080x760")
        self.root.minsize(940, 640)
        self.root.configure(bg=BG)

        self.filaments = fdb.get_filaments()
        self.image_path = None
        self.preview_img = None          # keep a reference to avoid GC
        self.extracted = []              # list of extracted color dicts
        self.results = []                # list of (color, matches) for export

        self.num_colors = IntVar(value=4)
        self.brand_var = StringVar(value="All")
        self.material_var = StringVar(value="All")

        self._build_ui()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self._build_header()
        self._build_controls()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        header = Frame(self.root, bg=BG_PANEL)
        header.pack(side=TOP, fill=X)
        Label(
            header, text="  🎨  3D Print Color Palette Matcher",
            bg=BG_PANEL, fg=FG, font=(FONT, 18, "bold"),
        ).pack(side=LEFT, padx=12, pady=12)
        Label(
            header, text="Extract image colors → match to real filaments  ",
            bg=BG_PANEL, fg=FG_MUTED, font=(FONT, 10),
        ).pack(side=RIGHT, padx=12)

    def _build_controls(self):
        bar = Frame(self.root, bg=BG)
        bar.pack(side=TOP, fill=X, padx=12, pady=(10, 4))

        self.load_btn = Button(
            bar, text="📂  Load Image", command=self.browse_image,
            bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
            activeforeground="white", relief="flat", font=(FONT, 10, "bold"),
            padx=14, pady=6, cursor="hand2", bd=0,
        )
        self.load_btn.pack(side=LEFT)

        # Number of colors
        Label(bar, text="Colors:", bg=BG, fg=FG, font=(FONT, 10)).pack(side=LEFT, padx=(18, 4))
        self.color_scale = Scale(
            bar, from_=1, to=16, orient=HORIZONTAL, variable=self.num_colors,
            bg=BG, fg=FG, highlightthickness=0, troughcolor=BG_CARD,
            activebackground=ACCENT, length=170, showvalue=True,
        )
        self.color_scale.pack(side=LEFT)

        # Brand filter
        Label(bar, text="Brand:", bg=BG, fg=FG, font=(FONT, 10)).pack(side=LEFT, padx=(18, 4))
        brands = ["All"] + fdb.get_brands()
        self._make_option(bar, self.brand_var, brands).pack(side=LEFT)

        # Material filter
        Label(bar, text="Material:", bg=BG, fg=FG, font=(FONT, 10)).pack(side=LEFT, padx=(12, 4))
        materials = ["All"] + fdb.get_materials()
        self._make_option(bar, self.material_var, materials).pack(side=LEFT)

        # Action buttons on the right
        self.export_btn = Button(
            bar, text="💾  Export", command=self.export_palette,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 10), padx=12, pady=6, cursor="hand2", bd=0,
            state="disabled",
        )
        self.export_btn.pack(side=RIGHT)

        self.match_btn = Button(
            bar, text="🔍  Match Colors", command=self.run_matching,
            bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
            activeforeground="white", relief="flat", font=(FONT, 10, "bold"),
            padx=14, pady=6, cursor="hand2", bd=0, state="disabled",
        )
        self.match_btn.pack(side=RIGHT, padx=(0, 8))

    def _make_option(self, parent, var, values):
        menu = OptionMenu(parent, var, *values)
        menu.configure(
            bg=BG_CARD, fg=FG, activebackground=ACCENT, activeforeground="white",
            relief="flat", font=(FONT, 10), highlightthickness=0, bd=0, width=12,
            cursor="hand2",
        )
        menu["menu"].configure(bg=BG_CARD, fg=FG, activebackground=ACCENT)
        return menu

    def _build_body(self):
        body = Frame(self.root, bg=BG)
        body.pack(side=TOP, fill=BOTH, expand=True, padx=12, pady=8)

        # Left: image preview / drop zone
        left = Frame(body, bg=BG_PANEL, width=340)
        left.pack(side=LEFT, fill=Y)
        left.pack_propagate(False)

        Label(left, text="Image", bg=BG_PANEL, fg=FG_MUTED,
              font=(FONT, 10, "bold")).pack(anchor=W, padx=12, pady=(10, 4))

        self.drop_zone = Frame(left, bg=BG_CARD, height=300)
        self.drop_zone.pack(fill=X, padx=12)
        self.drop_zone.pack_propagate(False)

        dnd_hint = ("Drag & drop an image here\nor click 'Load Image'"
                    if _DND_AVAILABLE else
                    "Click 'Load Image' to begin\n(install tkinterdnd2 for drag & drop)")
        self.preview_label = Label(
            self.drop_zone, text=dnd_hint, bg=BG_CARD, fg=FG_MUTED,
            font=(FONT, 10), justify="center", wraplength=280,
        )
        self.preview_label.pack(expand=True)

        if _DND_AVAILABLE:
            self.drop_zone.drop_target_register(DND_FILES)
            self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)

        self.path_label = Label(
            left, text="No image loaded", bg=BG_PANEL, fg=FG_MUTED,
            font=(FONT, 9), wraplength=310, justify="left",
        )
        self.path_label.pack(anchor=W, padx=12, pady=8)

        # Right: results (scrollable)
        right = Frame(body, bg=BG)
        right.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 0))

        Label(right, text="Palette & Filament Matches", bg=BG, fg=FG_MUTED,
              font=(FONT, 10, "bold")).pack(anchor=W, pady=(0, 4))

        canvas_wrap = Frame(right, bg=BG)
        canvas_wrap.pack(fill=BOTH, expand=True)

        self.results_canvas = Canvas(canvas_wrap, bg=BG, highlightthickness=0)
        scrollbar = Scrollbar(canvas_wrap, orient=VERTICAL, command=self.results_canvas.yview)
        self.results_inner = Frame(self.results_canvas, bg=BG)

        self.results_inner.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")),
        )
        self._inner_window = self.results_canvas.create_window((0, 0), window=self.results_inner, anchor="nw")
        self.results_canvas.bind(
            "<Configure>",
            lambda e: self.results_canvas.itemconfig(self._inner_window, width=e.width),
        )
        self.results_canvas.configure(yscrollcommand=scrollbar.set)

        self.results_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Mouse wheel scrolling
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.results_canvas.bind_all("<Button-4>", lambda e: self.results_canvas.yview_scroll(-1, "units"))
        self.results_canvas.bind_all("<Button-5>", lambda e: self.results_canvas.yview_scroll(1, "units"))

        self._show_placeholder()

    def _build_statusbar(self):
        self.status = StringVar(value="Ready. Load an image to start.")
        bar = Frame(self.root, bg=BG_PANEL)
        bar.pack(side=TOP, fill=X)
        Label(bar, textvariable=self.status, bg=BG_PANEL, fg=FG_MUTED,
              font=(FONT, 9), anchor=W).pack(side=LEFT, padx=12, pady=5)
        Label(bar, text=f"{len(self.filaments)} filaments  •  "
                        f"{len(fdb.get_brands())} brands",
              bg=BG_PANEL, fg=FG_MUTED, font=(FONT, 9)).pack(side=RIGHT, padx=12)

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #
    def _on_mousewheel(self, event):
        self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_drop(self, event):
        path = event.data.strip().strip("{}")
        if os.path.isfile(path):
            self.load_image(path)

    def browse_image(self):
        path = filedialog.askopenfilename(title="Select an image", filetypes=SUPPORTED_TYPES)
        if path:
            self.load_image(path)

    def load_image(self, path):
        try:
            img = Image.open(path)
            img.verify()  # validate it's a real image
            img = Image.open(path)  # reopen after verify
        except Exception as exc:
            messagebox.showerror("Invalid image", f"Could not open the image:\n{exc}")
            return

        self.image_path = path
        self._render_preview(img)
        self.path_label.config(text=os.path.basename(path))
        self.match_btn.config(state="normal")
        self.status.set(f"Loaded: {os.path.basename(path)} — click 'Match Colors'.")
        self._show_placeholder("Click '🔍 Match Colors' to analyze this image.")

    def _render_preview(self, img):
        thumb = img.convert("RGB").copy()
        thumb.thumbnail((300, 280), Image.LANCZOS)
        self.preview_img = ImageTk.PhotoImage(thumb)
        self.preview_label.config(image=self.preview_img, text="")

    # ------------------------------------------------------------------ #
    # Matching workflow
    # ------------------------------------------------------------------ #
    def run_matching(self):
        if not self.image_path:
            return
        self.match_btn.config(state="disabled")
        self.load_btn.config(state="disabled")
        self.status.set("Extracting colors…")
        # Run heavy work off the UI thread
        threading.Thread(target=self._do_matching, daemon=True).start()

    def _do_matching(self):
        try:
            n = self.num_colors.get()
            extracted = cu.extract_colors(self.image_path, n)
            brand = self.brand_var.get()
            material = self.material_var.get()

            results = []
            for color in extracted:
                matches = cu.match_filaments(
                    color["rgb"], self.filaments, top_n=3,
                    brand_filter=brand, material_filter=material,
                )
                results.append((color, matches))
            self.extracted = extracted
            self.results = results
            self.root.after(0, self._display_results)
        except Exception as exc:
            self.root.after(0, lambda: self._matching_error(exc))

    def _matching_error(self, exc):
        messagebox.showerror("Error", f"Something went wrong while matching:\n{exc}")
        self.status.set("Error during matching.")
        self.match_btn.config(state="normal")
        self.load_btn.config(state="normal")

    # ------------------------------------------------------------------ #
    # Results rendering
    # ------------------------------------------------------------------ #
    def _clear_results(self):
        for child in self.results_inner.winfo_children():
            child.destroy()

    def _show_placeholder(self, text="Your extracted palette and filament matches will appear here."):
        self._clear_results()
        Label(self.results_inner, text=text, bg=BG, fg=FG_MUTED,
              font=(FONT, 11), justify="center", wraplength=560).pack(pady=40)

    def _display_results(self):
        self._clear_results()
        no_match_note = ""
        for idx, (color, matches) in enumerate(self.results, start=1):
            self._build_color_card(idx, color, matches)
            if not matches:
                no_match_note = " (some colors had no filament in the selected filter)"

        self.match_btn.config(state="normal")
        self.load_btn.config(state="normal")
        self.export_btn.config(state="normal")
        self.status.set(
            f"Matched {len(self.results)} color(s) against {len(self.filaments)} filaments{no_match_note}."
        )
        self.results_canvas.yview_moveto(0)

    def _build_color_card(self, idx, color, matches):
        card = Frame(self.results_inner, bg=BG_CARD)
        card.pack(fill=X, pady=6, padx=2)

        # Header row: swatch + hex/rgb + prevalence
        head = Frame(card, bg=BG_CARD)
        head.pack(fill=X, padx=10, pady=(10, 6))

        swatch = Canvas(head, width=56, height=56, bg=color["hex"], highlightthickness=1,
                        highlightbackground="#11121a")
        swatch.pack(side=LEFT)

        info = Frame(head, bg=BG_CARD)
        info.pack(side=LEFT, padx=12)
        r, g, b = color["rgb"]
        Label(info, text=f"Color {idx}  •  {color['percentage']}% of image",
              bg=BG_CARD, fg=FG_MUTED, font=(FONT, 9)).pack(anchor=W)
        Label(info, text=color["hex"], bg=BG_CARD, fg=FG,
              font=(FONT, 13, "bold")).pack(anchor=W)
        Label(info, text=f"RGB({r}, {g}, {b})", bg=BG_CARD, fg=FG_MUTED,
              font=(FONT, 9)).pack(anchor=W)

        # Matches
        if not matches:
            Label(card, text="No filament match for the selected brand/material filter.",
                  bg=BG_CARD, fg="#e0a458", font=(FONT, 9, "italic")).pack(anchor=W, padx=12, pady=(0, 10))
            return

        for j, m in enumerate(matches):
            self._build_match_row(card, m, best=(j == 0))

    def _build_match_row(self, parent, m, best=False):
        row = Frame(parent, bg=BG_CARD)
        row.pack(fill=X, padx=12, pady=2)

        Canvas(row, width=26, height=26, bg=m["hex"], highlightthickness=1,
               highlightbackground="#11121a").pack(side=LEFT)

        quality = self._match_quality(m["distance"])
        label_txt = f"{m['brand']} — {m['name']}"
        sub_txt = f"{m['material']}  •  {m['hex']}  •  ΔE {m['distance']}  •  {quality}"

        text_wrap = Frame(row, bg=BG_CARD)
        text_wrap.pack(side=LEFT, padx=10, fill=X, expand=True)
        prefix = "★ " if best else "   "
        Label(text_wrap, text=prefix + label_txt, bg=BG_CARD,
              fg=(ACCENT if best else FG), font=(FONT, 10, "bold" if best else "normal"),
              anchor=W).pack(anchor=W)
        Label(text_wrap, text=sub_txt, bg=BG_CARD, fg=FG_MUTED,
              font=(FONT, 8), anchor=W).pack(anchor=W)

        Button(row, text="Buy ↗", command=lambda url=m["url"]: webbrowser.open(url),
               bg=BG_PANEL, fg=ACCENT, activebackground=ACCENT, activeforeground="white",
               relief="flat", font=(FONT, 9, "bold"), padx=10, pady=2, cursor="hand2",
               bd=0).pack(side=RIGHT)

    @staticmethod
    def _match_quality(distance):
        if distance <= 2:
            return "excellent match"
        if distance <= 5:
            return "great match"
        if distance <= 10:
            return "good match"
        if distance <= 20:
            return "fair match"
        return "approximate"

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #
    def export_palette(self):
        if not self.results:
            return
        path = filedialog.asksaveasfilename(
            title="Export palette",
            defaultextension=".json",
            filetypes=[("JSON file", "*.json"), ("Text file", "*.txt"),
                       ("HTML file", "*.html")],
            initialfile="filament_palette",
        )
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext == ".txt":
                self._export_txt(path)
            elif ext == ".html":
                self._export_html(path)
            else:
                self._export_json(path)
            self.status.set(f"Palette exported to {os.path.basename(path)}.")
            messagebox.showinfo("Exported", f"Palette saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))

    def _payload(self):
        data = []
        for color, matches in self.results:
            data.append({
                "extracted_color": {
                    "hex": color["hex"],
                    "rgb": color["rgb"],
                    "percentage": color["percentage"],
                },
                "matches": [
                    {
                        "brand": m["brand"], "material": m["material"],
                        "name": m["name"], "hex": m["hex"], "rgb": m["rgb"],
                        "delta_e": m["distance"], "url": m["url"],
                    } for m in matches
                ],
            })
        return {"source_image": os.path.basename(self.image_path or ""), "palette": data}

    def _export_json(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self._payload(), fh, indent=2)

    def _export_txt(self, path):
        lines = ["3D Print Color Palette Matcher — Export",
                 f"Source image: {os.path.basename(self.image_path or '')}", "=" * 50, ""]
        for i, (color, matches) in enumerate(self.results, 1):
            lines.append(f"Color {i}: {color['hex']}  RGB{color['rgb']}  ({color['percentage']}%)")
            if not matches:
                lines.append("   (no match for selected filter)")
            for m in matches:
                lines.append(f"   - {m['brand']} {m['name']} [{m['material']}] "
                             f"{m['hex']}  ΔE={m['distance']}  {m['url']}")
            lines.append("")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    def _export_html(self, path):
        rows = []
        for i, (color, matches) in enumerate(self.results, 1):
            match_html = ""
            for m in matches:
                match_html += (
                    f"<div style='display:flex;align-items:center;gap:8px;margin:4px 0'>"
                    f"<span style='width:20px;height:20px;background:{m['hex']};"
                    f"border:1px solid #ccc;display:inline-block'></span>"
                    f"<a href='{m['url']}' target='_blank'>{m['brand']} — {m['name']}</a>"
                    f"<span style='color:#666'>[{m['material']}] {m['hex']} · ΔE {m['distance']}</span></div>"
                )
            if not matches:
                match_html = "<em>No match for selected filter</em>"
            rows.append(
                f"<div style='border:1px solid #ddd;border-radius:8px;padding:12px;margin:10px 0'>"
                f"<div style='display:flex;align-items:center;gap:12px'>"
                f"<span style='width:48px;height:48px;background:{color['hex']};"
                f"border:1px solid #ccc;display:inline-block;border-radius:4px'></span>"
                f"<div><strong>Color {i}: {color['hex']}</strong><br>"
                f"<span style='color:#666'>RGB{color['rgb']} · {color['percentage']}% of image</span></div></div>"
                f"<div style='margin-top:8px'>{match_html}</div></div>"
            )
        html = (
            "<!doctype html><html><head><meta charset='utf-8'>"
            "<title>Filament Palette</title>"
            "<style>body{font-family:Segoe UI,Arial,sans-serif;max-width:720px;"
            "margin:24px auto;padding:0 16px;color:#222}</style></head><body>"
            f"<h1>3D Print Filament Palette</h1>"
            f"<p>Source image: {os.path.basename(self.image_path or '')}</p>"
            + "".join(rows) + "</body></html>"
        )
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)


def main():
    root = TkinterDnD.Tk() if _DND_AVAILABLE else Tk()
    ColorMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
