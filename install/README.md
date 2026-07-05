# Putting the app on your desktop 🖥️

Download the right file for your computer from the
[**Releases page**](https://github.com/Netspecs/3d-color-palette-matcher/releases),
then follow the steps for your operating system.

---

## 🪟 Windows

**Recommended — use the installer (⭐ easiest, adds a desktop icon + uninstaller):**
1. Download **`3DColorPaletteMatcher-Setup.exe`** from the Releases page.
2. Double-click it and follow the wizard (keep "Create a desktop icon" ticked).
3. Done! You now have:
   - 🖥️ A **desktop icon** with the app logo
   - 📂 A **Start Menu** entry
   - 🗑️ An entry in **Settings → Apps → Installed apps** (a.k.a. "Programs and
     Features") so you can **uninstall** it cleanly anytime.

> The installer doesn't need administrator rights — it installs just for your user.

---

**Alternative — the portable exe (no install):**

If you'd rather not install anything, download `3DColorPaletteMatcher-windows.exe`
and run it directly. This portable file **won't** create a desktop icon or appear in
"Programs and Features" on its own. To pin it to your desktop:
- Right-click it → **Show more options** → **Send to** → **Desktop (create shortcut)**, or
- Put `windows-create-desktop-shortcut.bat` in the same folder and double-click it.

> 💡 The first time you run either one, Windows SmartScreen may say "Windows protected
> your PC". Click **More info → Run anyway** (this happens for any app that isn't
> code-signed).

---

## 🍎 macOS

1. Download `3DColorPaletteMatcher-macos`.
2. Move it to your **Applications** folder.
3. Drag it onto your **Dock** to keep it there.

> 💡 The first time you open it, right-click the app → **Open** → **Open** to get past
> the "unidentified developer" warning (only needed once).

---

## 🐧 Linux

1. Put `linux-install.sh` in the **same folder** as `3DColorPaletteMatcher-linux`.
2. Open a terminal in that folder and run:
   ```bash
   bash linux-install.sh
   ```
3. The app now shows up in your applications menu **and** on your desktop, with its icon.
