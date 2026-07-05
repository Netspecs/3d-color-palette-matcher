#!/usr/bin/env bash
# =====================================================================
#  3D Color Palette Matcher - install a desktop launcher (Linux)
#
#  HOW TO USE:
#   1. Put this script in the SAME folder as 3DColorPaletteMatcher-linux
#   2. Open a terminal in that folder and run:
#          bash linux-install.sh
#   3. The app appears in your applications menu and on the desktop,
#      with its icon.
# =====================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Locate the executable (accept a couple of common names).
EXE=""
for cand in "3DColorPaletteMatcher-linux" "3DColorPaletteMatcher"; do
    if [ -f "$SCRIPT_DIR/$cand" ]; then EXE="$SCRIPT_DIR/$cand"; break; fi
done
if [ -z "$EXE" ]; then
    echo "Could not find the executable next to this script."
    echo "Keep linux-install.sh in the same folder as 3DColorPaletteMatcher-linux."
    exit 1
fi

chmod +x "$EXE"

# Install a copy of the icon (bundled inside the exe's docs folder if present,
# otherwise fall back to a shipped icon.png next to this script).
ICON_DIR="$HOME/.local/share/icons"
mkdir -p "$ICON_DIR"
ICON_DEST="$ICON_DIR/color-palette-matcher.png"
if [ -f "$SCRIPT_DIR/icon.png" ]; then
    cp "$SCRIPT_DIR/icon.png" "$ICON_DEST"
elif [ -f "$SCRIPT_DIR/../docs/icon.png" ]; then
    cp "$SCRIPT_DIR/../docs/icon.png" "$ICON_DEST"
else
    ICON_DEST=""   # no icon available; launcher still works
fi

# Build the .desktop launcher.
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
DESKTOP_FILE="$APPS_DIR/color-palette-matcher.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=3D Color Palette Matcher
Comment=Extract colors from an image and match them to 3D printing filaments
Exec=$EXE
Icon=${ICON_DEST:-applications-graphics}
Terminal=false
Categories=Graphics;Utility;
EOF

chmod +x "$DESKTOP_FILE"

# Also drop a copy on the Desktop if one exists.
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
if [ -d "$DESKTOP_DIR" ]; then
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/" 2>/dev/null || true
    chmod +x "$DESKTOP_DIR/color-palette-matcher.desktop" 2>/dev/null || true
    # Mark trusted for GNOME (best effort).
    gio set "$DESKTOP_DIR/color-palette-matcher.desktop" \
        metadata::trusted true 2>/dev/null || true
fi

update-desktop-database "$APPS_DIR" 2>/dev/null || true

echo "Done! '3D Color Palette Matcher' is now in your app menu"
echo "and on your Desktop."
