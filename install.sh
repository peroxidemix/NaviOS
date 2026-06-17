#!/bin/bash
set -e

INSTALL_DIR="$HOME/navi-ui"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HYPR_DIR="$HOME/.config/hypr"

NVIDIA=false
if lspci 2>/dev/null | grep -qi nvidia; then
    NVIDIA=true
fi

if command -v pacman >/dev/null; then
    read -p "Install dependencies via pacman? [y/N] " yn
    case "$yn" in
        [Yy]*)
            sudo pacman -S --needed --noconfirm \
                python python-gobject gtk3 gtk-layer-shell cairo \
                python-cairo webkit2gtk-4.1 python-pip \
                playerctl pamixer brightnessctl blueman \
                gst-plugins-good gst-plugins-bad gst-plugins-base
            pip install --break-system-packages --upgrade pywebview
            if $NVIDIA; then
                sudo pacman -S --needed --noconfirm nvidia-utils libva-nvidia-driver nvidia-dkms
            fi
            ;;
    esac
fi

if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    cp -r "$SCRIPT_DIR"/. "$INSTALL_DIR"/
    cd "$INSTALL_DIR"
fi

grep -rl "/home/drennant" . --include="*.py" --include="*.conf" --include="*.html" | while read -r f; do
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

if ! grep -q "navi-ui/launch.py" "$HYPR_DIR/hyprland.conf" 2>/dev/null; then
    if $NVIDIA; then
        printf "\nexec-once = GDK_BACKEND=x11 python3 $INSTALL_DIR/launch.py\nexec-once = GDK_BACKEND=x11 python3 $INSTALL_DIR/clock.py\nexec-once = GDK_BACKEND=x11 python3 $INSTALL_DIR/volumehud.py\nexec-once = GDK_BACKEND=x11 python3 $INSTALL_DIR/brightnesshud.py\nexec-once = GDK_BACKEND=x11 python3 $INSTALL_DIR/workspaceglitch.py\nexec-once = bash -c \"mkfifo /tmp/quickmenu_pipe 2>/dev/null; GDK_BACKEND=x11 python3 $INSTALL_DIR/quickmenu/evdev_listener.py\"\n" >> "$HYPR_DIR/hyprland.conf"
    else
        printf "\nexec-once = python3 $INSTALL_DIR/launch.py\nexec-once = python3 $INSTALL_DIR/clock.py\nexec-once = python3 $INSTALL_DIR/volumehud.py\nexec-once = python3 $INSTALL_DIR/brightnesshud.py\nexec-once = python3 $INSTALL_DIR/workspaceglitch.py\nexec-once = bash -c \"mkfifo /tmp/quickmenu_pipe 2>/dev/null; python3 $INSTALL_DIR/quickmenu/evdev_listener.py\"\n" >> "$HYPR_DIR/hyprland.conf"
    fi
    echo "added exec-once lines to hyprland.conf"
else
    echo "exec-once lines already present in hyprland.conf"
fi

if $NVIDIA; then
    if [ -f /etc/default/grub ] && ! grep -q "nvidia-drm.modeset=1" /etc/default/grub; then
        sudo sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"/GRUB_CMDLINE_LINUX_DEFAULT="\1 nvidia-drm.modeset=1"/' /etc/default/grub
        sudo grub-mkconfig -o /boot/grub/grub.cfg
        echo "added nvidia-drm.modeset=1 to grub"
    fi
    if ! grep -q "GBM_BACKEND=nvidia-drm" /etc/environment 2>/dev/null; then
        printf "\nGBM_BACKEND=nvidia-drm\n__GLX_VENDOR_LIBRARY_NAME=nvidia\nWLR_NO_HARDWARE_CURSORS=1\n" | sudo tee -a /etc/environment > /dev/null
        echo "added nvidia env vars to /etc/environment"
    fi
fi

chmod +x "$INSTALL_DIR"/*.sh "$INSTALL_DIR"/hypr-config/*.sh "$HYPR_DIR"/*.sh 2>/dev/null || true

echo "done - reboot to start Navi OS"
