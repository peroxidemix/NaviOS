import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, GtkLayerShell, GLib
import subprocess, json

win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.TOP, True)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.LEFT, True)
GtkLayerShell.set_exclusive_zone(win, 0)

screen = win.get_screen()
visual = screen.get_rgba_visual()
if visual and screen.is_composited():
    win.set_visual(visual)
win.set_app_paintable(True)

box = Gtk.Box()
box.get_style_context().add_class("kittybar")
win.add(box)

css = Gtk.CssProvider()
css.load_from_data(b"""
    .kittybar {
        background-color: rgba(64, 224, 200, 0.35);
        min-height: 24px;
    }
""")
Gtk.StyleContext.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def update_position():
    out = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True, text=True).stdout
    clients = json.loads(out)
    kitty = next((c for c in clients if c["class"] == "kitty"), None)
    if kitty:
        x, y = kitty["at"]
        w, h = kitty["size"]
        GtkLayerShell.set_margin(win, GtkLayerShell.Edge.LEFT, x)
        GtkLayerShell.set_margin(win, GtkLayerShell.Edge.TOP, y)
        win.set_size_request(w, 24)
        win.show()
    else:
        win.hide()
    return True

GLib.timeout_add(300, update_position)
win.show_all()
Gtk.main()
