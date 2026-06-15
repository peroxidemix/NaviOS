# NaviOS

my Hyprland setup, themed around Navi from Serial Experiments Lain

## install

```sh
git clone https://github.com/peroxidemix/NaviOS.git
cd NaviOS
./install.sh
```

if you're on arch it'll offer to install everything for you. on other distros grab these first: Hyprland, python-gobject (GTK3 + GtkLayerShell), pywebview, cairo, webkit2gtk, playerctl, pamixer, brightnessctl, blueman - then run the script.

it copies itself to ~/navi-ui, fixes the paths for your home dir, and drops the hypr configs into ~/.config/hypr. won't touch anything that's already there so merge your keybinds/monitors/autostart by hand if you've got existing configs.

set up monitors.conf for your display then restart Hyprland.

MIT licensed
