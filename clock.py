import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib

win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)
GtkLayerShell.set_exclusive_zone(win, 0)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.NONE)

screen = win.get_screen()
visual = screen.get_rgba_visual()
if visual and screen.is_composited():
    win.set_visual(visual)
win.set_app_paintable(True)

webview = WebKit2.WebView()
webview.set_background_color(Gdk.RGBA(0,0,0,0))
webview.load_uri("file:///home/drennant/navi-ui/clock.html")
win.set_default_size(220, 70)
win.add(webview)
win.show_all()
win.input_shape_combine_region(__import__('cairo').Region())

import threading, time

def get_bytes():
    total = 0
    with open('/proc/net/dev') as f:
        for line in f.readlines()[2:]:
            parts = line.split()
            if parts[0].startswith('lo:'):
                continue
            total += int(parts[1]) + int(parts[9])
    return total

def net_watcher():
    last = get_bytes()
    while True:
        time.sleep(1)
        cur = get_bytes()
        active = (cur - last) > 5000
        last = cur
        GLib.idle_add(lambda a=active: webview.run_javascript(f"window.setNetActive({'true' if a else 'false'})"))

threading.Thread(target=net_watcher, daemon=True).start()
Gtk.main()
