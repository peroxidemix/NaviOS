#!/bin/bash
set -e

INSTALL_DIR="$HOME/navi-ui"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HYPR_DIR="$HOME/.config/hypr"

if command -v pacman >/dev/null; then
    read -p "Install dependencies via pacman? [y/N] " yn
    case "$yn" in
        [Yy]*)
            sudo pacman -S --needed --noconfirm \
                python python-gobject gtk3 gtk-layer-shell cairo \
                python-cairo webkit2gtk python-pip \
                playerctl pamixer brightnessctl blueman
            pip install --break-system-packages --upgrade pywebview
            ;;
    esac
fi

if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/. "$INSTALL_DIR"/
    cd "$INSTALL_DIR"
fi

grep -rl "/home/drennant" . --include="*.py" --include="*.conf" | while read -r f; do
    sed -i "s|/home/drennant/navi-ui|$INSTALL_DIR|g; s|/home/drennant|$HOME|g" "$f"
done

mkdir -p "$HYPR_DIR/scripts"

for f in hypr-config/*.conf hypr-config/*.sh; do
    name="$(basename "$f")"
    if [ -f "$HYPR_DIR/$name" ]; then
        echo "skip $name (already exists)"
    else
        cp "$f" "$HYPR_DIR/$name"
        echo "copied $name"
    fi
done

for f in hypr-config/scripts/*.py; do
    name="$(basename "$f")"
    cp "$f" "$HYPR_DIR/scripts/$name"
    sed -i "s|/home/drennant/navi-ui|$INSTALL_DIR|g; s|/home/drennant|$HOME|g" "$HYPR_DIR/scripts/$name"
    echo "copied scripts/$name"
done

chmod +x "$INSTALL_DIR"/*.sh "$INSTALL_DIR"/hypr-config/*.sh "$HYPR_DIR"/*.sh 2>/dev/null || true

echo "done - check $HYPR_DIR/monitors.conf for your display, then restart Hyprland"
