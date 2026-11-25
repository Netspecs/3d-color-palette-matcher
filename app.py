"""
3D Print Color Palette Matcher
==============================

A desktop application that extracts the dominant colors from an image (or takes
colors you type in directly) and matches them to real-world 3D printing filament
colors from popular brands (Bambu Lab, Hatchbox, Prusament, eSun, Polymaker, and
more), covering PLA, PETG, ABS, TPU, Silk, Matte and Wood.

Matching uses the perceptual CIEDE2000 color-difference formula. It can plan
slot assignments for multi-material systems (Bambu AMS, Prusa MMU3, tool
changers / multi-head, IDEX / dual, or manual swaps) and render a preview of
your image in the matched filament colors.

Run with:  python app.py
"""

import json
import os
import sys
import threading
import webbrowser
from tkinter import (
    Tk, Frame, Label, Button, Canvas, StringVar, IntVar, DoubleVar, BooleanVar,
    OptionMenu, Entry, Text, Toplevel, Listbox, Scale, Spinbox, Checkbutton,
    HORIZONTAL, filedialog, messagebox, simpledialog, colorchooser, Scrollbar,
    LEFT, RIGHT, BOTH, X, Y, TOP, BOTTOM, W, E, VERTICAL, END, SINGLE,
)
from tkinter import ttk

import numpy as np
from PIL import Image, ImageTk

import color_utils as cu
import filament_database as fdb
import cost as cost_calc
import palette_store as pstore
import slicer_export as sexport

APP_VERSION = "2.1"

# Optional AI background removal — used ONLY if the user already has it installed.
# It is never a required dependency (keeps PyInstaller builds small).
try:
    import rembg  # noqa: F401
    _REMBG_AVAILABLE = True
except Exception:
    _REMBG_AVAILABLE = False

# Working resolution for the analysis/mask image (longest side, px).
WORK_MAX_DIM = 480
# Max size of the on-screen interactive preview canvas.
CANVAS_W, CANVAS_H = 316, 300

# ---------------------------------------------------------------------------
# Multi-material print systems for the Print Planner.
#   slots  : fixed number of filament slots (None = derived / custom)
#   shared : True if all colors share ONE nozzle (=> purge/wipe waste on every
#            tool change). False for independent-nozzle systems (IDEX, tool
#            changers) which have little to no purge waste.
# ---------------------------------------------------------------------------
PRINT_SYSTEMS = {
    "Bambu AMS — 4 slots": {"slots": 4, "shared": True},
    "Bambu AMS — 8 slots (2× AMS)": {"slots": 8, "shared": True},
    "Bambu AMS — 16 slots (4× AMS)": {"slots": 16, "shared": True},
    "Prusa MMU3 — 5 slots": {"slots": 5, "shared": True},
    "Tool changer / Multi-head": {"slots": None, "shared": False, "custom": True,
                                  "default": 4, "max": 8},
    "IDEX / Dual extruder — 2 slots": {"slots": 2, "shared": False},
    "Manual filament swaps": {"slots": None, "shared": False, "manual": True},
}

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
        self.root.title(f"3D Print Color Palette Matcher v{APP_VERSION}")
        self.root.geometry("1000x720")
        self.root.minsize(900, 620)
        self.root.configure(bg=BG)
        self._set_window_icon()

        self.filaments = fdb.get_filaments()
        self.image_path = None
        self.preview_img = None          # keep a reference to avoid GC
        self.extracted = []              # list of extracted color dicts
        self.results = []                # list of (color, matches) for export

        # --- Background removal / mask state (v2.1) ---
        self.work_arr = None             # (H,W,3) uint8 analysis image
        self.disp_arr = None             # (h,w,3) uint8 on-screen thumbnail
        self.disp_tk = None              # PhotoImage ref for the canvas
        self.disp_box = (0, 0, 0, 0)     # (x, y, w, h) image placement on canvas
        self.excluded_colors = []        # list of (r,g,b) removed as background
        self.crop_norm = None            # (x0,y0,x1,y1) in 0-1, or None
        self.ai_mask = None              # optional rembg subject mask (work res)
        self.interaction_mode = StringVar(value="none")  # none|remove|eyedrop|crop
        self.mask_tol = DoubleVar(value=18.0)            # ΔE (Lab) removal tolerance
        self.show_mask = BooleanVar(value=True)
        self._crop_drag = None           # transient (x0,y0) during a crop drag

        self.num_colors = IntVar(value=4)
        self.brand_var = StringVar(value="All")
        self.material_var = StringVar(value="All")
        self.brightness = DoubleVar(value=1.0)
        self.saturation = DoubleVar(value=1.0)
        self.grams_var = StringVar(value="50")

        self._build_ui()

    # ------------------------------------------------------------------ #
    # Window icon
    # ------------------------------------------------------------------ #
    def _resource_path(self, *parts):
        """Resolve a bundled resource path both from source and when frozen."""
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, *parts)

    def _set_window_icon(self):
        """Give the window/taskbar the app icon (best-effort, cross-platform)."""
        # Windows: use the .ico for the title bar / taskbar if present.
        try:
            ico = self._resource_path("docs", "icon.ico")
            if os.name == "nt" and os.path.exists(ico):
                self.root.iconbitmap(ico)
        except Exception:
            pass
        # All platforms: set a PNG icon photo (works on Linux/macOS too).
        try:
            png = self._resource_path("docs", "icon.png")
            if os.path.exists(png):
                self._icon_img = ImageTk.PhotoImage(Image.open(png))
                self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        self._build_header()
        self._build_controls()
        self._build_controls_row2()
        self._build_controls_row3()
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

        self.hex_btn = Button(
            bar, text="🎨  Enter Colors", command=self.enter_colors_dialog,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 10), padx=12, pady=6, cursor="hand2", bd=0,
        )
        self.hex_btn.pack(side=LEFT, padx=(8, 0))

        # Number of colors
        Label(bar, text="Colors:", bg=BG, fg=FG, font=(FONT, 10)).pack(side=LEFT, padx=(18, 4))
        self.color_scale = Scale(
            bar, from_=1, to=16, orient=HORIZONTAL, variable=self.num_colors,
            bg=BG, fg=FG, highlightthickness=0, troughcolor=BG_CARD,
            activebackground=ACCENT, length=170, showvalue=True,
        )
        self.color_scale.pack(side=LEFT)

        # Primary action on the right — kept alone so it never collides with
        # the filters on narrower windows. Export/other actions live on row 3.
        self.match_btn = Button(
            bar, text="🔍  Match Colors", command=self.run_matching,
            bg=ACCENT, fg="white", activebackground=ACCENT_DARK,
            activeforeground="white", relief="flat", font=(FONT, 10, "bold"),
            padx=14, pady=6, cursor="hand2", bd=0, state="disabled",
        )
        self.match_btn.pack(side=RIGHT, padx=(0, 8))

    def _build_controls_row2(self):
        bar = Frame(self.root, bg=BG)
        bar.pack(side=TOP, fill=X, padx=12, pady=(0, 4))

        # Brand filter
        Label(bar, text="Brand:", bg=BG, fg=FG, font=(FONT, 9)).pack(side=LEFT, padx=(0, 4))
        brands = ["All"] + fdb.get_brands()
        self._make_option(bar, self.brand_var, brands).pack(side=LEFT)

        # Material filter
        Label(bar, text="Material:", bg=BG, fg=FG, font=(FONT, 9)).pack(side=LEFT, padx=(12, 4))
        materials = ["All"] + fdb.get_materials()
        self._make_option(bar, self.material_var, materials).pack(side=LEFT)

        # Brightness / saturation adjustment (applied to extracted colors)
        Label(bar, text="Brightness:", bg=BG, fg=FG, font=(FONT, 9)).pack(side=LEFT, padx=(18, 2))
        Scale(bar, from_=0.5, to=1.5, resolution=0.05, orient=HORIZONTAL,
              variable=self.brightness, bg=BG, fg=FG, highlightthickness=0,
              troughcolor=BG_CARD, activebackground=ACCENT, length=110,
              showvalue=True).pack(side=LEFT)

        Label(bar, text="Saturation:", bg=BG, fg=FG, font=(FONT, 9)).pack(side=LEFT, padx=(12, 2))
        Scale(bar, from_=0.0, to=2.0, resolution=0.05, orient=HORIZONTAL,
              variable=self.saturation, bg=BG, fg=FG, highlightthickness=0,
              troughcolor=BG_CARD, activebackground=ACCENT, length=110,
              showvalue=True).pack(side=LEFT)

        # Print weight for the cost estimate
        Label(bar, text="Print weight (g):", bg=BG, fg=FG,
              font=(FONT, 9)).pack(side=LEFT, padx=(16, 2))
        grams_entry = Entry(bar, textvariable=self.grams_var, width=6, bg=BG_CARD,
                            fg=FG, insertbackground=FG, relief="flat",
                            font=(FONT, 10), justify="center")
        grams_entry.pack(side=LEFT)
        grams_entry.bind("<Return>", lambda e: self._refresh_cost())

    def _build_controls_row3(self):
        """Result/action buttons — kept on their own row so nothing collides
        with the tuning controls on narrower windows."""
        bar = Frame(self.root, bg=BG)
        bar.pack(side=TOP, fill=X, padx=12, pady=(0, 6))

        Label(bar, text="Results:", bg=BG, fg=FG_MUTED,
              font=(FONT, 9)).pack(side=LEFT, padx=(0, 4))

        # Print planner + filament preview (enabled once colors are matched)
        self.preview_btn = Button(
            bar, text="🖼️  Filament Preview", command=self.open_filament_preview,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 9), padx=10, pady=4, cursor="hand2", bd=0,
            state="disabled",
        )
        self.preview_btn.pack(side=LEFT, padx=(0, 8))

        self.plan_btn = Button(
            bar, text="🖨️  Plan Print", command=self.open_planner,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 9), padx=10, pady=4, cursor="hand2", bd=0,
            state="disabled",
        )
        self.plan_btn.pack(side=LEFT, padx=(0, 8))

        # Saved palettes
        self.save_btn = Button(
            bar, text="⭐  Save Palette", command=self.save_current_palette,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 9), padx=10, pady=4, cursor="hand2", bd=0,
            state="disabled",
        )
        self.save_btn.pack(side=RIGHT)

        self.load_pal_btn = Button(
            bar, text="📁  Saved Palettes", command=self.open_saved_palettes,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 9), padx=10, pady=4, cursor="hand2", bd=0,
        )
        self.load_pal_btn.pack(side=RIGHT, padx=(0, 8))

        self.export_btn = Button(
            bar, text="💾  Export", command=self.export_palette,
            bg=BG_CARD, fg=FG, activebackground=BG_PANEL, activeforeground=FG,
            relief="flat", font=(FONT, 9), padx=10, pady=4, cursor="hand2", bd=0,
            state="disabled",
        )
        self.export_btn.pack(side=RIGHT, padx=(0, 8))

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

        # Left: interactive image preview / drop zone + background tools
        left = Frame(body, bg=BG_PANEL, width=340)
        left.pack(side=LEFT, fill=Y)
        left.pack_propagate(False)

        Label(left, text="Image", bg=BG_PANEL, fg=FG_MUTED,
              font=(FONT, 10, "bold")).pack(anchor=W, padx=12, pady=(10, 4))

        self.drop_zone = Frame(left, bg=BG_CARD, width=CANVAS_W, height=CANVAS_H)
        self.drop_zone.pack(padx=12)
        self.drop_zone.pack_propagate(False)

        # The preview is now a Canvas so we can click/drag on the image for
        # background removal, the eyedropper and crop selection.
        self.img_canvas = Canvas(self.drop_zone, bg=BG_CARD, highlightthickness=0,
                                 width=CANVAS_W, height=CANVAS_H, cursor="arrow")
        self.img_canvas.pack(fill=BOTH, expand=True)
        dnd_hint = ("Drag & drop an image here\nor click 'Load Image'"
                    if _DND_AVAILABLE else
                    "Click 'Load Image' to begin\n(install tkinterdnd2\nfor drag & drop)")
        self._canvas_hint = self.img_canvas.create_text(
            CANVAS_W // 2, CANVAS_H // 2, text=dnd_hint, fill=FG_MUTED,
            font=(FONT, 10), justify="center", width=CANVAS_W - 30,
        )
        self.img_canvas.bind("<Button-1>", self._on_canvas_press)
        self.img_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.img_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        if _DND_AVAILABLE:
            self.img_canvas.drop_target_register(DND_FILES)
            self.img_canvas.dnd_bind("<<Drop>>", self._on_drop)

        self._build_mask_tools(left)

        self.path_label = Label(
            left, text="No image loaded", bg=BG_PANEL, fg=FG_MUTED,
            font=(FONT, 9), wraplength=310, justify="left",
        )
        self.path_label.pack(anchor=W, padx=12, pady=(6, 8))

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
    # Background-removal tools (v2.1)
    # ------------------------------------------------------------------ #
    def _build_mask_tools(self, parent):
        tools = Frame(parent, bg=BG_PANEL)
        tools.pack(fill=X, padx=12, pady=(8, 0))
        Label(tools, text="Background removal & tools", bg=BG_PANEL, fg=FG_MUTED,
              font=(FONT, 9, "bold")).pack(anchor=W)

        self.mode_buttons = {}

        def _mode_btn(parent, label, mode):
            b = Button(parent, text=label, command=lambda m=mode: self._set_mode(m),
                       bg=BG_CARD, fg=FG, activebackground=ACCENT,
                       activeforeground="white", relief="flat", font=(FONT, 8),
                       padx=6, pady=3, cursor="hand2", bd=0)
            b.pack(side=LEFT, padx=(0, 4))
            self.mode_buttons[mode] = b
            return b

        row1 = Frame(tools, bg=BG_PANEL)
        row1.pack(fill=X, pady=(5, 2))
        _mode_btn(row1, "🩹 Pick-remove", "remove")
        _mode_btn(row1, "💧 Eyedropper", "eyedrop")
        _mode_btn(row1, "⬚ Crop", "crop")

        row2 = Frame(tools, bg=BG_PANEL)
        row2.pack(fill=X, pady=2)
        Button(row2, text="✨ Auto BG", command=self._auto_remove_bg, bg=BG_CARD,
               fg=FG, activebackground=ACCENT, activeforeground="white",
               relief="flat", font=(FONT, 8), padx=6, pady=3, cursor="hand2",
               bd=0).pack(side=LEFT, padx=(0, 4))
        if _REMBG_AVAILABLE:
            Button(row2, text="🤖 AI cut-out", command=self._ai_remove_bg, bg=BG_CARD,
                   fg=FG, activebackground=ACCENT, activeforeground="white",
                   relief="flat", font=(FONT, 8), padx=6, pady=3, cursor="hand2",
                   bd=0).pack(side=LEFT, padx=(0, 4))
        Button(row2, text="↺ Reset", command=self._reset_mask, bg=BG_CARD,
               fg="#e0a458", activebackground=BG_PANEL, activeforeground="#e0a458",
               relief="flat", font=(FONT, 8), padx=6, pady=3, cursor="hand2",
               bd=0).pack(side=LEFT, padx=(0, 4))

        row3 = Frame(tools, bg=BG_PANEL)
        row3.pack(fill=X, pady=(2, 0))
        Label(row3, text="Tolerance", bg=BG_PANEL, fg=FG_MUTED,
              font=(FONT, 8)).pack(side=LEFT)
        Scale(row3, from_=2, to=45, resolution=1, orient=HORIZONTAL,
              variable=self.mask_tol, command=lambda *_: self._on_tol_change(),
              bg=BG_PANEL, fg=FG, highlightthickness=0, troughcolor=BG_CARD,
              activebackground=ACCENT, length=120, showvalue=True,
              font=(FONT, 7)).pack(side=LEFT, padx=(2, 6))
        Checkbutton(row3, text="Show removed", variable=self.show_mask,
                    command=self._update_canvas, bg=BG_PANEL, fg=FG_MUTED,
                    selectcolor=BG_CARD, activebackground=BG_PANEL,
                    activeforeground=FG, font=(FONT, 8), bd=0,
                    highlightthickness=0).pack(side=LEFT)

        self._set_mode("none")

    def _set_mode(self, mode):
        """Toggle an interaction mode (clicking the active one turns it off)."""
        if self.interaction_mode.get() == mode and mode != "none":
            mode = "none"
        self.interaction_mode.set(mode)
        for m, btn in self.mode_buttons.items():
            active = (m == mode)
            btn.config(bg=ACCENT if active else BG_CARD,
                       fg="white" if active else FG)
        cursors = {"remove": "target", "eyedrop": "dotbox", "crop": "crosshair"}
        try:
            self.img_canvas.config(cursor=cursors.get(mode, "arrow"))
        except Exception:
            pass
        hints = {
            "remove": "Click the background/plate to remove that color everywhere.",
            "eyedrop": "Click a spot to add that exact color to your palette.",
            "crop": "Drag a rectangle to analyze only that region.",
            "none": "",
        }
        if hints.get(mode):
            self.status.set(hints[mode])

    def _on_tol_change(self):
        # Re-render the live mask preview as the tolerance slider moves.
        if self.work_arr is not None:
            self._update_canvas()

    def _current_exclusions(self):
        tol = float(self.mask_tol.get())
        return [{"rgb": c, "tol": tol} for c in self.excluded_colors]

    def _auto_remove_bg(self):
        if self.work_arr is None:
            messagebox.showinfo("No image", "Load an image first.")
            return
        bg_colors = cu.estimate_background_colors(self.work_arr, n_colors=3)
        added = 0
        for c in bg_colors:
            if c not in self.excluded_colors:
                self.excluded_colors.append(c)
                added += 1
        self._update_canvas()
        self.status.set(f"Auto background: excluded {added} border color(s). "
                        "Use Pick-remove or Tolerance to fine-tune, then Match.")

    def _ai_remove_bg(self):
        """Optional AI subject cut-out (only if rembg is installed)."""
        if self.work_arr is None:
            return
        try:
            from rembg import remove
            out = remove(Image.fromarray(self.work_arr))
            alpha = np.asarray(out.convert("RGBA"))[:, :, 3]
            self.ai_mask = alpha > 128
            self._update_canvas()
            self.status.set("AI cut-out applied — only the subject is kept.")
        except Exception as exc:
            messagebox.showerror("AI cut-out failed", str(exc))

    def _reset_mask(self):
        self.excluded_colors = []
        self.crop_norm = None
        self.ai_mask = None
        self._update_canvas()
        self.status.set("Background selection reset — the whole image is analyzed.")

    # --- canvas coordinate mapping & sampling --- #
    def _canvas_to_disp(self, cx, cy):
        x, y, w, h = self.disp_box
        dx, dy = int(cx - x), int(cy - y)
        if 0 <= dx < w and 0 <= dy < h:
            return dx, dy
        return None

    def _sample_color(self, cx, cy):
        pos = self._canvas_to_disp(cx, cy)
        if pos is None or self.disp_arr is None:
            return None
        dx, dy = pos
        return tuple(int(v) for v in self.disp_arr[dy, dx])

    def _on_canvas_press(self, event):
        if self.work_arr is None:
            return
        mode = self.interaction_mode.get()
        if mode == "remove":
            rgb = self._sample_color(event.x, event.y)
            if rgb and rgb not in self.excluded_colors:
                self.excluded_colors.append(rgb)
                self._update_canvas()
                self.status.set(f"Removing color {cu.rgb_to_hex(rgb)} "
                                f"({len(self.excluded_colors)} removed). Re-match to apply.")
        elif mode == "eyedrop":
            rgb = self._sample_color(event.x, event.y)
            if rgb:
                self._add_eyedropper_color(rgb)
        elif mode == "crop":
            pos = self._canvas_to_disp(event.x, event.y)
            if pos is not None:
                self._crop_drag = (event.x, event.y)

    def _on_canvas_drag(self, event):
        if self.interaction_mode.get() == "crop" and self._crop_drag:
            self.img_canvas.delete("cropsel")
            x0, y0 = self._crop_drag
            self.img_canvas.create_rectangle(x0, y0, event.x, event.y,
                                             outline=ACCENT, width=2, tags="cropsel")

    def _on_canvas_release(self, event):
        if self.interaction_mode.get() == "crop" and self._crop_drag:
            x0, y0 = self._crop_drag
            self._crop_drag = None
            p0 = self._clamp_to_disp(x0, y0)
            p1 = self._clamp_to_disp(event.x, event.y)
            x, y, w, h = self.disp_box
            if abs(p1[0] - p0[0]) < 5 or abs(p1[1] - p0[1]) < 5:
                return  # ignore tiny drags
            self.crop_norm = (
                (p0[0]) / w, (p0[1]) / h, (p1[0]) / w, (p1[1]) / h,
            )
            self._update_canvas()
            self.status.set("Crop set — only the selected region will be analyzed. "
                            "Re-match to apply.")

    def _clamp_to_disp(self, cx, cy):
        x, y, w, h = self.disp_box
        return (min(max(cx - x, 0), w), min(max(cy - y, 0), h))

    def _add_eyedropper_color(self, rgb):
        color = {"rgb": rgb, "hex": cu.rgb_to_hex(rgb), "percentage": 0.0,
                 "added": True}
        matches = cu.match_filaments(rgb, self.filaments, top_n=3,
                                     brand_filter=self.brand_var.get(),
                                     material_filter=self.material_var.get())
        self.extracted.append(color)
        self.results.append((color, matches))
        self._display_results()
        self.status.set(f"Added {cu.rgb_to_hex(rgb)} from the image to your palette.")

    # --- mask computation & canvas rendering --- #
    def _display_keep_mask(self):
        """Keep-mask at display resolution (True = kept)."""
        if self.disp_arr is None:
            return None
        mask = cu.compute_keep_mask(self.disp_arr, self._current_exclusions(),
                                    self.crop_norm)
        ai = getattr(self, "ai_mask", None)
        if ai is not None:
            ai_disp = np.asarray(Image.fromarray(ai.astype(np.uint8) * 255)
                                 .resize((mask.shape[1], mask.shape[0]),
                                         Image.NEAREST)) > 128
            mask &= ai_disp
        return mask

    def _update_canvas(self):
        """Redraw the preview image with the mask overlay and crop rectangle."""
        self.img_canvas.delete("all")
        if self.disp_arr is None:
            self._canvas_hint = self.img_canvas.create_text(
                CANVAS_W // 2, CANVAS_H // 2,
                text="Click 'Load Image' to begin", fill=FG_MUTED,
                font=(FONT, 10), justify="center")
            return

        disp = self.disp_arr.copy()
        h, w = disp.shape[:2]
        if self.show_mask.get():
            keep = self._display_keep_mask()
            if keep is not None and not keep.all():
                removed = ~keep
                # Checkerboard dim for removed pixels so it's obvious what's cut.
                yy, xx = np.mgrid[0:h, 0:w]
                check = (((xx // 6) + (yy // 6)) % 2).astype(bool)
                dark = np.array([40, 42, 54], dtype=np.uint8)
                light = np.array([70, 72, 86], dtype=np.uint8)
                overlay = np.where(check[..., None], light, dark)
                disp[removed] = (0.25 * disp[removed]
                                 + 0.75 * overlay[removed]).astype(np.uint8)

        self.disp_tk = ImageTk.PhotoImage(Image.fromarray(disp))
        x = (CANVAS_W - w) // 2
        y = (CANVAS_H - h) // 2
        self.disp_box = (x, y, w, h)
        self.img_canvas.create_image(x, y, anchor="nw", image=self.disp_tk)

        if self.crop_norm:
            x0, y0, x1, y1 = self.crop_norm
            self.img_canvas.create_rectangle(
                x + x0 * w, y + y0 * h, x + x1 * w, y + y1 * h,
                outline=ACCENT, width=2, dash=(4, 2))

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
        # Build the analysis-resolution working array and the on-screen thumbnail.
        self.work_arr = cu.load_rgb_array(path, WORK_MAX_DIM)
        self._render_preview(img)
        # Loading a new image clears any previous background selection.
        self.excluded_colors = []
        self.crop_norm = None
        self.ai_mask = None
        self._set_mode("none")
        self._update_canvas()
        self.path_label.config(text=os.path.basename(path))
        self.match_btn.config(state="normal")
        self.status.set(f"Loaded: {os.path.basename(path)} — remove the background "
                        "if needed, then click 'Match Colors'.")
        self._show_placeholder("Click '🔍 Match Colors' to analyze this image.")

    def _render_preview(self, img):
        thumb = img.convert("RGB").copy()
        thumb.thumbnail((CANVAS_W, CANVAS_H), Image.LANCZOS)
        self.disp_arr = np.asarray(thumb, dtype=np.uint8)

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
            extracted = self._extract_with_mask(n)

            # Optional brightness / saturation tweak on the extracted colors
            bright = self.brightness.get()
            sat = self.saturation.get()
            if abs(bright - 1.0) > 1e-3 or abs(sat - 1.0) > 1e-3:
                for color in extracted:
                    adj = cu.adjust_rgb(color["rgb"], brightness=bright, saturation=sat)
                    color["rgb"] = adj
                    color["hex"] = cu.rgb_to_hex(adj)

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
            self.root.after(0, lambda e=exc: self._matching_error(e))

    def _extract_with_mask(self, n):
        """Extract palette colors from the working image, honoring the mask/crop."""
        if self.work_arr is None:
            return cu.extract_colors(self.image_path, n)
        keep = cu.compute_keep_mask(self.work_arr, self._current_exclusions(),
                                    self.crop_norm)
        if self.ai_mask is not None and self.ai_mask.shape == keep.shape:
            keep &= self.ai_mask
        pixels = self.work_arr.reshape(-1, 3)[keep.reshape(-1)]
        # Safety: if the selection removed (almost) everything, fall back to all.
        if pixels.shape[0] < 50:
            pixels = self.work_arr.reshape(-1, 3)
        return cu.extract_colors_from_pixels(pixels, n)

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
        self._build_cost_card()
        no_match_note = ""
        for idx, (color, matches) in enumerate(self.results, start=1):
            self._build_color_card(idx, color, matches)
            if not matches:
                no_match_note = " (some colors had no filament in the selected filter)"

        self.match_btn.config(state="normal")
        self.load_btn.config(state="normal")
        self.export_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.plan_btn.config(state="normal" if self.results else "disabled")
        # Filament preview needs the original image file on disk.
        can_preview = bool(self.image_path) and os.path.isfile(self.image_path or "")
        self.preview_btn.config(state="normal" if can_preview else "disabled")
        self.status.set(
            f"Matched {len(self.results)} color(s) against {len(self.filaments)} filaments{no_match_note}."
        )
        self.results_canvas.yview_moveto(0)

    def _remove_color(self, color_ref):
        """Drop one extracted color from the results, cost and planner."""
        self.results = [(c, m) for (c, m) in self.results if c is not color_ref]
        self.extracted = [c for c in self.extracted if c is not color_ref]
        if self.results:
            self._display_results()
            self.status.set("Removed a color from the palette.")
        else:
            self._show_placeholder("All colors removed. Match an image or enter colors.")
            for btn in (self.export_btn, self.save_btn, self.plan_btn,
                        self.preview_btn):
                btn.config(state="disabled")

    def _parse_grams(self):
        try:
            return max(0.0, float(self.grams_var.get()))
        except (ValueError, TypeError):
            return 0.0

    def _build_cost_card(self):
        """Render the estimated filament cost summary at the top of results."""
        grams = self._parse_grams()
        estimate = cost_calc.estimate_costs(self.results, grams)

        card = Frame(self.results_inner, bg=BG_PANEL)
        card.pack(fill=X, pady=(2, 8), padx=2)

        top = Frame(card, bg=BG_PANEL)
        top.pack(fill=X, padx=12, pady=(10, 4))
        Label(top, text="💰  Estimated filament cost", bg=BG_PANEL, fg=FG,
              font=(FONT, 11, "bold")).pack(side=LEFT)
        Label(top, text=f"${estimate['total_cost']:.2f}", bg=BG_PANEL, fg=ACCENT,
              font=(FONT, 13, "bold")).pack(side=RIGHT)

        Label(card, text=f"For a {estimate['total_grams']:.0f} g print, using the best "
                         f"match per color (edit 'Print weight' above and re-match to update).",
              bg=BG_PANEL, fg=FG_MUTED, font=(FONT, 8), justify="left",
              wraplength=560).pack(anchor=W, padx=12, pady=(0, 8))

        for row in estimate["breakdown"]:
            line = Frame(card, bg=BG_PANEL)
            line.pack(fill=X, padx=12, pady=1)
            Canvas(line, width=16, height=16, bg=row["hex"], highlightthickness=1,
                   highlightbackground="#11121a").pack(side=LEFT)
            Label(line, text=f"  {row['percentage']:.0f}%  •  {row['grams']:.1f} g  •  {row['filament']}",
                  bg=BG_PANEL, fg=FG_MUTED, font=(FONT, 8), anchor=W).pack(side=LEFT)
            Label(line, text=f"${row['cost']:.2f}", bg=BG_PANEL, fg=FG,
                  font=(FONT, 9)).pack(side=RIGHT)
        Frame(card, bg=BG_PANEL, height=6).pack()

    def _refresh_cost(self):
        """Re-render results (recomputes cost) when the weight changes."""
        if self.results:
            self._display_results()

    def _build_color_card(self, idx, color, matches):
        card = Frame(self.results_inner, bg=BG_CARD)
        card.pack(fill=X, pady=6, padx=2)

        # Header row: swatch + hex/rgb + prevalence
        head = Frame(card, bg=BG_CARD)
        head.pack(fill=X, padx=10, pady=(10, 6))

        swatch = Canvas(head, width=56, height=56, bg=color["hex"], highlightthickness=1,
                        highlightbackground="#11121a")
        swatch.pack(side=LEFT)

        # Remove-this-color (✕) button so a wrong/background color can be
        # dropped from the matches, cost estimate and planner.
        Button(head, text="✕", command=lambda c=color: self._remove_color(c),
               bg=BG_CARD, fg="#e06c6c", activebackground=BG_PANEL,
               activeforeground="#e06c6c", relief="flat", font=(FONT, 11, "bold"),
               padx=6, pady=0, cursor="hand2", bd=0).pack(side=RIGHT, anchor="n")

        info = Frame(head, bg=BG_CARD)
        info.pack(side=LEFT, padx=12)
        r, g, b = color["rgb"]
        src = "  •  added from image" if color.get("added") else " of image"
        pct_txt = (f"Color {idx}  •  {color['percentage']}%{src}"
                   if not color.get("added")
                   else f"Color {idx}{src}")
        Label(info, text=pct_txt,
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
        # Thresholds calibrated for CIEDE2000 (ΔE2000), which runs noticeably
        # smaller than the old CIE76 metric. Rough perceptual guide:
        #   ΔE2000 < 1   -> difference not perceptible to the human eye
        #   1-2          -> perceptible only on close inspection
        #   2-3.5        -> perceptible at a glance
        #   3.5-6        -> clearly different but a reasonable substitute
        if distance <= 1:
            return "perfect match"
        if distance <= 2:
            return "excellent match"
        if distance <= 3.5:
            return "great match"
        if distance <= 6:
            return "good match"
        if distance <= 10:
            return "fair match"
        return "approximate"

    # ------------------------------------------------------------------ #
    # Direct color input (no image required)
    # ------------------------------------------------------------------ #
    def enter_colors_dialog(self):
        """Let the user type/paste hex colors or pick them, then match."""
        win = Toplevel(self.root)
        win.title("Enter Colors")
        win.configure(bg=BG)
        win.geometry("420x460")
        win.transient(self.root)
        win.grab_set()

        Label(win, text="Enter colors manually", bg=BG, fg=FG,
              font=(FONT, 13, "bold")).pack(anchor=W, padx=14, pady=(12, 2))
        Label(win, text="Paste or type hex codes (one per line, or separated by\n"
                        "commas/spaces). Example:  #E63946  1D3557  #A8DADC",
              bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left").pack(anchor=W, padx=14)

        text = Text(win, height=9, bg=BG_CARD, fg=FG, insertbackground=FG,
                    relief="flat", font=("Consolas", 11), wrap="word")
        text.pack(fill=X, padx=14, pady=8)
        text.focus_set()

        # Live-updating swatch preview of the parsed colors
        swatch_wrap = Frame(win, bg=BG)
        swatch_wrap.pack(fill=X, padx=14)
        Label(swatch_wrap, text="Preview:", bg=BG, fg=FG_MUTED,
              font=(FONT, 9)).pack(side=LEFT)
        swatch_row = Frame(swatch_wrap, bg=BG)
        swatch_row.pack(side=LEFT, padx=6)

        def _refresh_swatches(*_):
            for c in swatch_row.winfo_children():
                c.destroy()
            for rgb in self._parse_hex_text(text.get("1.0", END))[:16]:
                Canvas(swatch_row, width=20, height=20, bg=cu.rgb_to_hex(rgb),
                       highlightthickness=1, highlightbackground="#11121a").pack(side=LEFT, padx=1)

        text.bind("<KeyRelease>", _refresh_swatches)

        def _pick_color():
            rgb, hex_str = colorchooser.askcolor(parent=win, title="Pick a color")
            if hex_str:
                current = text.get("1.0", END).strip()
                text.insert(END, ("\n" if current else "") + hex_str.upper())
                _refresh_swatches()

        def _apply():
            colors = self._parse_hex_text(text.get("1.0", END))
            if not colors:
                messagebox.showwarning("No colors", "Please enter at least one valid "
                                       "hex color (e.g. #FF8800).", parent=win)
                return
            win.destroy()
            self._match_manual_colors(colors)

        btns = Frame(win, bg=BG)
        btns.pack(fill=X, padx=14, pady=12, side=BOTTOM)
        Button(btns, text="🎨  Pick a color…", command=_pick_color, bg=BG_CARD, fg=FG,
               activebackground=BG_PANEL, activeforeground=FG, relief="flat",
               font=(FONT, 10), padx=12, pady=5, cursor="hand2", bd=0).pack(side=LEFT)
        Button(btns, text="Match Colors", command=_apply, bg=ACCENT, fg="white",
               activebackground=ACCENT_DARK, activeforeground="white", relief="flat",
               font=(FONT, 10, "bold"), padx=14, pady=5, cursor="hand2", bd=0).pack(side=RIGHT)
        Button(btns, text="Cancel", command=win.destroy, bg=BG_CARD, fg=FG,
               activebackground=BG_PANEL, activeforeground=FG, relief="flat",
               font=(FONT, 10), padx=12, pady=5, cursor="hand2", bd=0).pack(side=RIGHT, padx=8)

    @staticmethod
    def _parse_hex_text(raw):
        """Parse free-form text into a list of (r, g, b) tuples, ignoring junk."""
        import re
        tokens = re.split(r"[\s,;]+", raw.strip())
        colors = []
        for tok in tokens:
            if not tok:
                continue
            try:
                colors.append(cu.hex_to_rgb(tok))
            except ValueError:
                continue
        return colors

    def _match_manual_colors(self, colors):
        """Build a palette from hand-entered colors and match to filaments."""
        n = len(colors)
        share = round(100.0 / n, 1) if n else 0.0
        extracted = [
            {"rgb": rgb, "hex": cu.rgb_to_hex(rgb), "percentage": share}
            for rgb in colors
        ]

        brand = self.brand_var.get()
        material = self.material_var.get()
        results = []
        for color in extracted:
            matches = cu.match_filaments(
                color["rgb"], self.filaments, top_n=3,
                brand_filter=brand, material_filter=material,
            )
            results.append((color, matches))

        # Manual colors aren't tied to an image file.
        self.image_path = None
        self.preview_img = None
        self.work_arr = None
        self.disp_arr = None
        self.excluded_colors = []
        self.crop_norm = None
        self.ai_mask = None
        self.img_canvas.delete("all")
        self.img_canvas.create_text(CANVAS_W // 2, CANVAS_H // 2,
                                    text="Colors entered manually\n(no image)",
                                    fill=FG_MUTED, font=(FONT, 10), justify="center")
        self.path_label.config(text=f"{n} color(s) entered manually")
        self.extracted = extracted
        self.results = results
        self.num_colors.set(min(16, max(1, n)))
        self._display_results()

    # ------------------------------------------------------------------ #
    # Print system planner
    # ------------------------------------------------------------------ #
    def open_planner(self):
        """Assign the matched colors to the slots of a chosen print system."""
        if not self.results:
            return
        win = Toplevel(self.root)
        win.title("Print System Planner")
        win.configure(bg=BG)
        win.geometry("660x640")
        win.transient(self.root)

        Label(win, text="🖨️  Print System Planner", bg=BG, fg=FG,
              font=(FONT, 14, "bold")).pack(anchor=W, padx=16, pady=(14, 2))
        Label(win, text="Assign your matched colors to filament slots. Colors are "
                        "ordered by how much of the image they cover.",
              bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left",
              wraplength=610).pack(anchor=W, padx=16)

        ctrl = Frame(win, bg=BG)
        ctrl.pack(fill=X, padx=16, pady=10)

        Label(ctrl, text="System:", bg=BG, fg=FG, font=(FONT, 10)).pack(side=LEFT)
        system_var = StringVar(value=next(iter(PRINT_SYSTEMS)))
        opt = OptionMenu(ctrl, system_var, *PRINT_SYSTEMS.keys())
        opt.configure(bg=BG_CARD, fg=FG, activebackground=ACCENT,
                      activeforeground="white", relief="flat", font=(FONT, 10),
                      highlightthickness=0, bd=0, width=26, cursor="hand2")
        opt["menu"].configure(bg=BG_CARD, fg=FG, activebackground=ACCENT)
        opt.pack(side=LEFT, padx=8)

        heads_lbl = Label(ctrl, text="Heads:", bg=BG, fg=FG, font=(FONT, 10))
        heads_var = IntVar(value=4)
        heads_spin = Spinbox(ctrl, from_=2, to=8, width=4, textvariable=heads_var,
                             bg=BG_CARD, fg=FG, buttonbackground=BG_CARD,
                             relief="flat", font=(FONT, 10), justify="center")

        plan_area = Frame(win, bg=BG)
        plan_area.pack(fill=BOTH, expand=True, padx=16, pady=(4, 12))

        def _toggle_heads(*_):
            spec = PRINT_SYSTEMS[system_var.get()]
            if spec.get("custom"):
                heads_lbl.pack(side=LEFT, padx=(12, 2))
                heads_spin.pack(side=LEFT)
            else:
                heads_lbl.pack_forget()
                heads_spin.pack_forget()
            _render_plan()

        def _render_plan():
            for c in plan_area.winfo_children():
                c.destroy()
            spec = PRINT_SYSTEMS[system_var.get()]
            n_colors = len(self.results)

            if spec.get("manual"):
                slots = n_colors
            elif spec.get("custom"):
                slots = int(heads_var.get())
            else:
                slots = spec["slots"]

            plan, overflow = self._build_slot_plan(slots, spec.get("manual", False))

            # Summary line (fixed height, top)
            summary = (f"{n_colors} color(s) → {len(plan)} slot(s) used"
                       + (f", {slots} available" if not spec.get("manual") else ""))
            Label(plan_area, text=summary, bg=BG, fg=FG,
                  font=(FONT, 10, "bold")).pack(side=TOP, anchor=W, pady=(0, 6))

            # Notes (fixed height, bottom). Packed BEFORE the expanding slot
            # list so the list fills the remaining space and the notes keep
            # their strip at the bottom.
            notes = Frame(plan_area, bg=BG)
            notes.pack(side=BOTTOM, fill=X)

            # Scrollable slot list — canvas + scrollbar isolated in their own
            # frame so the LEFT/RIGHT packing can't fight the TOP/BOTTOM
            # packing of the summary and notes (which previously stopped the
            # canvas from expanding to full width).
            list_frame = Frame(plan_area, bg=BG)
            list_frame.pack(side=TOP, fill=BOTH, expand=True)

            canv = Canvas(list_frame, bg=BG, highlightthickness=0)
            sb = Scrollbar(list_frame, orient=VERTICAL, command=canv.yview)
            inner = Frame(canv, bg=BG)
            inner.bind("<Configure>", lambda e: canv.configure(scrollregion=canv.bbox("all")))
            iw = canv.create_window((0, 0), window=inner, anchor="nw")

            # Keep the embedded frame (and its rows) as wide as the canvas so
            # filament names never clip.
            def _fit(_e=None):
                w = canv.winfo_width()
                canv.itemconfig(iw, width=w if w > 1 else 600)

            canv.itemconfig(iw, width=600)
            canv.bind("<Configure>", _fit)
            canv.configure(yscrollcommand=sb.set)
            canv.pack(side=LEFT, fill=BOTH, expand=True)
            sb.pack(side=RIGHT, fill=Y)
            win.after(50, _fit)

            for slot_no, (color, match) in enumerate(plan, start=1):
                self._build_slot_row(inner, slot_no, color, match)

            if overflow:
                Label(notes, text=f"⚠️  {len(overflow)} color(s) don't fit in "
                                  f"{slots} slots. Reduce the color count, or print "
                                  f"the extras with a manual swap.",
                      bg=BG, fg="#e0a458", font=(FONT, 9), justify="left",
                      wraplength=610).pack(anchor=W, pady=(8, 0))
            if spec.get("shared"):
                Label(notes, text="💧  Shared-nozzle system: every color change purges "
                                  "filament into a waste/wipe tower. Fewer colors and "
                                  "grouping similar shades reduces waste.",
                      bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left",
                      wraplength=610).pack(anchor=W, pady=(6, 0))
            elif spec.get("manual"):
                Label(notes, text="🔁  Manual swaps: pause the print and change filament "
                                  "at the right layer. Almost no purge waste, but needs "
                                  "you to be present for each change.",
                      bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left",
                      wraplength=610).pack(anchor=W, pady=(6, 0))
            else:
                Label(notes, text="✅  Independent-nozzle system: each head prints its own "
                                  "color with little to no purge waste.",
                      bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left",
                      wraplength=610).pack(anchor=W, pady=(6, 0))

        system_var.trace_add("write", _toggle_heads)
        heads_var.trace_add("write", lambda *a: _render_plan())
        _toggle_heads()

    def _build_slot_plan(self, slots, manual):
        """Return (plan, overflow) where plan is a list of (color, best_match)."""
        plan = []
        overflow = []
        for i, (color, matches) in enumerate(self.results):
            best = matches[0] if matches else None
            if manual or i < slots:
                plan.append((color, best))
            else:
                overflow.append((color, best))
        return plan, overflow

    def _build_slot_row(self, parent, slot_no, color, match):
        row = Frame(parent, bg=BG_CARD)
        row.pack(fill=X, pady=3, padx=2)

        Label(row, text=f"Slot {slot_no}", bg=BG_CARD, fg=FG_MUTED,
              font=(FONT, 9, "bold"), width=7, anchor=W).pack(side=LEFT, padx=(10, 4), pady=8)

        # Target extracted color
        Canvas(row, width=30, height=30, bg=color["hex"], highlightthickness=1,
               highlightbackground="#11121a").pack(side=LEFT, pady=6)
        Label(row, text="→", bg=BG_CARD, fg=FG_MUTED, font=(FONT, 11)).pack(side=LEFT, padx=6)

        if match:
            Canvas(row, width=30, height=30, bg=match["hex"], highlightthickness=1,
                   highlightbackground="#11121a").pack(side=LEFT, pady=6)
            info = Frame(row, bg=BG_CARD)
            info.pack(side=LEFT, padx=10, fill=X, expand=True)
            Label(info, text=f"{match['brand']} — {match['name']}", bg=BG_CARD, fg=FG,
                  font=(FONT, 10, "bold"), anchor=W).pack(anchor=W)
            Label(info, text=f"{match['material']}  •  {match['hex']}  •  "
                             f"{color['percentage']}% of image  •  ΔE {match['distance']}",
                  bg=BG_CARD, fg=FG_MUTED, font=(FONT, 8), anchor=W).pack(anchor=W)
        else:
            Label(row, text="(no filament match in current filter)", bg=BG_CARD,
                  fg="#e0a458", font=(FONT, 9, "italic")).pack(side=LEFT, padx=10)

    # ------------------------------------------------------------------ #
    # Filament preview (posterized re-render)
    # ------------------------------------------------------------------ #
    def open_filament_preview(self):
        """Re-render the loaded image using the best-match filament colors."""
        if not self.image_path or not os.path.isfile(self.image_path):
            messagebox.showinfo("No image", "Filament preview needs a loaded image.")
            return
        if not self.results:
            return
        try:
            original, rendered = self._render_filament_image()
        except Exception as exc:
            messagebox.showerror("Preview failed", str(exc))
            return

        win = Toplevel(self.root)
        win.title("Filament Preview")
        win.configure(bg=BG)
        win.transient(self.root)

        Label(win, text="🖼️  What it looks like in filament colors", bg=BG, fg=FG,
              font=(FONT, 13, "bold")).pack(anchor=W, padx=16, pady=(14, 2))
        Label(win, text="Left: your image.   Right: re-rendered using the best-match "
                        "filament color for each palette color.",
              bg=BG, fg=FG_MUTED, font=(FONT, 9), justify="left",
              wraplength=640).pack(anchor=W, padx=16, pady=(0, 8))

        imgs = Frame(win, bg=BG)
        imgs.pack(padx=16, pady=8)

        self._orig_tk = ImageTk.PhotoImage(original)
        self._rendered_tk = ImageTk.PhotoImage(rendered)
        col1 = Frame(imgs, bg=BG)
        col1.pack(side=LEFT, padx=8)
        Label(col1, text="Original", bg=BG, fg=FG_MUTED, font=(FONT, 9)).pack()
        Label(col1, image=self._orig_tk, bg=BG).pack()
        col2 = Frame(imgs, bg=BG)
        col2.pack(side=LEFT, padx=8)
        Label(col2, text="Filament preview", bg=BG, fg=FG_MUTED, font=(FONT, 9)).pack()
        Label(col2, image=self._rendered_tk, bg=BG).pack()

        def _save():
            path = filedialog.asksaveasfilename(
                title="Save filament preview", defaultextension=".png",
                filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg")],
                initialfile="filament_preview",
            )
            if path:
                rendered.save(path)
                messagebox.showinfo("Saved", f"Preview saved to:\n{path}", parent=win)

        btns = Frame(win, bg=BG)
        btns.pack(fill=X, padx=16, pady=12)
        Button(btns, text="💾  Save preview image", command=_save, bg=ACCENT, fg="white",
               activebackground=ACCENT_DARK, activeforeground="white", relief="flat",
               font=(FONT, 10, "bold"), padx=14, pady=5, cursor="hand2", bd=0).pack(side=LEFT)
        Button(btns, text="Close", command=win.destroy, bg=BG_CARD, fg=FG,
               activebackground=BG_PANEL, activeforeground=FG, relief="flat",
               font=(FONT, 10), padx=12, pady=5, cursor="hand2", bd=0).pack(side=RIGHT)

    def _render_filament_image(self, max_dim=340):
        """
        Return (original_thumb, filament_thumb) PIL images.

        Each pixel is snapped to the nearest extracted palette color (in CIE Lab)
        and repainted with that color's best-match filament color, producing a
        posterized 'what it would look like printed' preview.
        """
        img = Image.open(self.image_path)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, img).convert("RGB")
        else:
            img = img.convert("RGB")
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        original = img.copy()

        img_arr = np.asarray(img)
        shape = img_arr.shape
        arr = img_arr.astype(np.float64).reshape(-1, 3)

        palette_rgb = np.array([c["rgb"] for c, _ in self.results], dtype=np.float64)
        # Best-match filament color per palette color (fall back to the color itself)
        target_rgb = np.array([
            (m[0]["rgb"] if m else c["rgb"])
            for c, m in self.results
        ], dtype=np.float64)

        # Nearest palette color for each pixel, measured in Lab space.
        px_lab = cu.rgb_to_lab(arr)
        pal_lab = cu.rgb_to_lab(palette_rgb)
        # Euclidean distance in Lab (fast, ample for a visual preview)
        diff = px_lab[:, None, :] - pal_lab[None, :, :]
        d2 = np.einsum("ijk,ijk->ij", diff, diff)
        nearest = np.argmin(d2, axis=1)

        out = target_rgb[nearest].reshape(*shape)

        # Respect the background mask/crop: removed areas are shown as a neutral
        # checkerboard instead of being repainted, so the preview matches what
        # actually gets analyzed and printed.
        keep = cu.compute_keep_mask(img_arr, self._current_exclusions(),
                                    self.crop_norm)
        if self.ai_mask is not None:
            ai_disp = np.asarray(Image.fromarray(self.ai_mask.astype(np.uint8) * 255)
                                 .resize((shape[1], shape[0]), Image.NEAREST)) > 128
            keep &= ai_disp
        if not keep.all():
            h, w = shape[:2]
            yy, xx = np.mgrid[0:h, 0:w]
            check = (((xx // 8) + (yy // 8)) % 2).astype(bool)
            board = np.where(check[..., None], np.array([70, 72, 86]),
                             np.array([45, 47, 60])).astype(np.float64)
            removed = ~keep
            out[removed] = board[removed]

        rendered = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
        return original, rendered

    # ------------------------------------------------------------------ #
    # Export
    # ------------------------------------------------------------------ #
    def export_palette(self):
        if not self.results:
            return
        path = filedialog.asksaveasfilename(
            title="Export palette",
            defaultextension=".json",
            filetypes=[
                ("JSON file", "*.json"),
                ("Readable text", "*.txt"),
                ("HTML page", "*.html"),
                ("CSV spreadsheet", "*.csv"),
                ("GIMP/Inkscape palette", "*.gpl"),
                ("Slicer filament config", "*.ini"),
            ],
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
            elif ext in (".csv", ".gpl", ".ini"):
                sexport.export_to_file(path, self.results)
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
                        "price_per_kg": m.get("price_per_kg"),
                    } for m in matches
                ],
            })
        estimate = cost_calc.estimate_costs(self.results, self._parse_grams())
        return {
            "source_image": os.path.basename(self.image_path or ""),
            "cost_estimate": estimate,
            "palette": data,
        }

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

    # ------------------------------------------------------------------ #
    # Saved / favorite palettes
    # ------------------------------------------------------------------ #
    def save_current_palette(self):
        if not self.results:
            return
        name = simpledialog.askstring(
            "Save palette", "Name this palette:", parent=self.root,
            initialvalue=os.path.splitext(os.path.basename(self.image_path or "My palette"))[0],
        )
        if not name:
            return
        try:
            pstore.save_palette(name, self._payload())
            self.status.set(f"Saved palette '{name}'.")
            messagebox.showinfo("Saved", f"Palette '{name}' saved.\n"
                                          "Open it any time from 'Saved Palettes'.")
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))

    def open_saved_palettes(self):
        names = pstore.list_names()
        win = Toplevel(self.root)
        win.title("Saved Palettes")
        win.configure(bg=BG)
        win.geometry("380x360")
        win.transient(self.root)

        Label(win, text="Saved Palettes", bg=BG, fg=FG,
              font=(FONT, 12, "bold")).pack(anchor=W, padx=12, pady=(12, 6))

        if not names:
            Label(win, text="No palettes saved yet.\nMatch an image and click "
                            "'⭐ Save Palette' to store one.",
                  bg=BG, fg=FG_MUTED, font=(FONT, 10), justify="left").pack(padx=12, pady=20)
            return

        listbox = Listbox(win, selectmode=SINGLE, bg=BG_CARD, fg=FG,
                          selectbackground=ACCENT, relief="flat", font=(FONT, 10),
                          highlightthickness=0, activestyle="none")
        for n in names:
            listbox.insert(END, n)
        listbox.pack(fill=BOTH, expand=True, padx=12, pady=6)
        listbox.selection_set(0)

        btns = Frame(win, bg=BG)
        btns.pack(fill=X, padx=12, pady=(0, 12))

        def _selected_name():
            sel = listbox.curselection()
            return listbox.get(sel[0]) if sel else None

        def _load():
            name = _selected_name()
            if name:
                self._load_palette_record(pstore.get_palette(name))
                win.destroy()

        def _delete():
            name = _selected_name()
            if name and messagebox.askyesno("Delete", f"Delete palette '{name}'?", parent=win):
                pstore.delete_palette(name)
                listbox.delete(listbox.curselection()[0])

        Button(btns, text="Open", command=_load, bg=ACCENT, fg="white",
               activebackground=ACCENT_DARK, activeforeground="white", relief="flat",
               font=(FONT, 10, "bold"), padx=12, pady=4, cursor="hand2", bd=0).pack(side=LEFT)
        Button(btns, text="Delete", command=_delete, bg=BG_CARD, fg="#e06c6c",
               activebackground=BG_PANEL, activeforeground="#e06c6c", relief="flat",
               font=(FONT, 10), padx=12, pady=4, cursor="hand2", bd=0).pack(side=LEFT, padx=8)
        Button(btns, text="Close", command=win.destroy, bg=BG_CARD, fg=FG,
               activebackground=BG_PANEL, activeforeground=FG, relief="flat",
               font=(FONT, 10), padx=12, pady=4, cursor="hand2", bd=0).pack(side=RIGHT)

    def _load_palette_record(self, record):
        """Rebuild the results view from a stored palette record."""
        if not record:
            return
        results = []
        for entry in record.get("palette", []):
            ec = entry.get("extracted_color", {})
            color = {
                "hex": ec.get("hex", "#000000"),
                "rgb": tuple(ec.get("rgb", (0, 0, 0))),
                "percentage": ec.get("percentage", 0),
            }
            matches = []
            for m in entry.get("matches", []):
                match = dict(m)
                match["rgb"] = tuple(m.get("rgb", (0, 0, 0)))
                match["distance"] = m.get("delta_e", m.get("distance", 0))
                match.setdefault(
                    "price_per_kg",
                    fdb.get_price_per_kg(m.get("brand", ""), m.get("material", "")),
                )
                matches.append(match)
            results.append((color, matches))

        self.results = results
        self.extracted = [c for c, _ in results]
        self.image_path = record.get("source_image", "") or self.image_path
        self.path_label.config(text=f"Loaded palette: {record.get('name', '')}")
        self._display_results()
        self.export_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.status.set(f"Loaded saved palette '{record.get('name', '')}'.")


def main():
    root = TkinterDnD.Tk() if _DND_AVAILABLE else Tk()
    ColorMatcherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
