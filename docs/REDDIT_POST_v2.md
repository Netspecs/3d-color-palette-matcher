# Reddit announcement — v2.0

Below are ready-to-paste posts for r/BambuLab, r/3Dprinting, and r/prusa3d.
Attach **docs/v2_showcase.png** (or the individual screenshots) as the image.

---

## 🎯 Title options (pick one)

- **[Free tool] I made a desktop app that turns any image into a 3D-print filament palette — now with a slot planner + filament preview (v2.0)**
- **My free "image → real filament colors" matcher got a big v2.0: AMS/MMU3 slot planner, filament preview, TPU/Silk/Matte/Wood, and way better color accuracy**
- **v2.0 of my free filament color-matcher: plan your AMS slots, preview the print in real filament colors, 225 filaments**

---

## 📝 Body (r/BambuLab / r/3Dprinting)

A while back I shared a little desktop app that extracts the dominant colors from
an image and matches them to **real filament colors** you can actually buy. Tons of
great feedback — so here's **v2.0**, which is a pretty big upgrade:

**🎨 What's new**

- **Much better color accuracy** — matching now uses **CIEDE2000** (the modern
  perceptual color-difference standard) instead of the older CIE76. Blues, reds
  and near-neutrals match noticeably better.
- **🖨️ Print System Planner** — pick your setup (Bambu **AMS 4/8/16**, **Prusa
  MMU3**, **tool changer / multi-head**, **IDEX / dual**, or **manual swaps**) and
  it assigns each color to a slot, warns you if you have more colors than slots,
  and reminds you about purge/waste on shared-nozzle systems.
- **🖼️ Filament Preview** — re-renders your image using only the matched filament
  colors, so you can see roughly what the print will look like *before* you commit.
- **➕ Bigger database — 225 filaments across 7 materials.** Added real **TPU,
  Silk, Matte and Wood** lines (Bambu, Polymaker, Overture, SUNLU, eSun, ColorFabb)
  on top of the existing PLA/PETG/ABS.
- **✏️ Direct color input** — no image? Just paste hex codes (or use the color
  picker) and match directly.

It also still shows a **cost estimate** for the print and **"Buy" links** for each
matched filament, and exports to JSON/TXT/HTML.

**💻 Free, open source, cross-platform** (Windows / macOS / Linux). Windows folks
can grab the one-click installer from the Releases page — no Python needed.

👉 **GitHub:** https://github.com/Netspecs/3d-color-palette-matcher
👉 **Download v2.0:** https://github.com/Netspecs/3d-color-palette-matcher/releases/tag/v2.0

Would love feedback — especially which **brands/materials** you'd like added next,
and whether the slot planner matches how you actually plan multi-color prints. 🙏

---

## 📝 Body variant (r/prusa3d — lead with MMU3)

Sharing a free, open-source desktop tool I built: it takes any image (or hex codes
you type in) and matches the colors to **real filament colors you can buy**, then
helps you plan a multi-color print.

**v2.0** just landed and it now understands the **Prusa MMU3 (5 slots)** directly —
the new **Print Planner** assigns each extracted color to a slot and flags when you
have more colors than slots. Other highlights:

- **CIEDE2000** perceptual matching for much better accuracy
- **Filament Preview** — see your image rendered in the matched filament colors
- **225 filaments / 7 materials** (added TPU, Silk, Matte, Wood)
- Cost estimate + buy links + JSON/TXT/HTML export

Free, cross-platform, no account. Feedback very welcome!

👉 https://github.com/Netspecs/3d-color-palette-matcher

---

## 💬 Ready replies for common comments

- **"Does it work offline?"** → Yep, 100% offline. The filament database is bundled;
  the only time it touches the internet is if you click a "Buy" link.
- **"Can you add <brand/material>?"** → Please open an issue (or PR) on GitHub with
  the brand + color name + hex — the database is just a Python list, super easy to extend.
- **"Colors look slightly off vs the real spool."** → Filament color is an
  approximation (screen vs. real, lighting, translucency). The ΔE number next to each
  match tells you how close it is; lower = closer.
- **"Mac/Linux build?"** → Both are built by CI on each release; check the Releases page.

---

## 📌 Posting tips

- Best days/times for r/BambuLab & r/3Dprinting: weekday mornings (US).
- Lead with the **image** (v2_showcase.png) — visual posts do far better.
- Reply to early comments quickly; it boosts visibility.
- Flair: use **"Show and Tell"** / **"Free Tool"** / **"Software"** where available.
- Don't cross-post all subs the same minute; space them out a few hours.
