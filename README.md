# NaviOS

My Hyprland setup themed around the Navi computer from Serial Experiments Lain. GTK3/WebKit2 homescreen, radial quickmenu, overlay HUDs for clock/volume/brightness, a music widget, workspace glitch effects, and a Copland OS style boot splash.

## Install

```sh
git clone https://github.com/nnndree-ctrl/NaviOS.git
cd NaviOS
./install.sh
```

On Arch/pacman it'll offer to install everything needed. On other distros, install these first: Hyprland, python-gobject (GTK3 + GtkLayerShell), pywebview, cairo, webkit2gtk, playerctl, pamixer, brightnessctl, blueman - then run the script.

It installs to ~/navi-ui, fixes paths for your home dir, and drops the hypr configs into ~/.config/hypr (won't overwrite anything already there, so merge keybinds/monitors/autostart by hand if needed).

Set up monitors.conf for your display, then restart Hyprland.

MIT licensed.
