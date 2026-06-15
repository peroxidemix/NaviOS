import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import subprocess, re, threading, time

win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.NONE)

screen = win.get_screen()
visual = screen.get_rgba_visual()
if visual and screen.is_composited():
    win.set_visual(visual)
win.set_app_paintable(True)

webview = WebKit2.WebView()
webview.set_background_color(Gdk.RGBA(0,0,0,0))
webview.load_uri("file:///home/drennant/navi-ui/brightnesshud.html")
win.add(webview)
win.show_all()
win.input_shape_combine_region(__import__('cairo').Region())

def get_brightness():
    cur = subprocess.run(["brightnessctl", "g"], capture_output=True, text=True).stdout.strip()
    mx = subprocess.run(["brightnessctl", "m"], capture_output=True, text=True).stdout.strip()
    try:
        pct = int(int(cur) / int(mx) * 100)
    except Exception:
        pct = 0
    return pct

import os, time as _t
LOCK = "/tmp/hud_lock"
def acquire_lock():
    try:
        if os.path.exists(LOCK):
            age = _t.time() - os.path.getmtime(LOCK)
            with open(LOCK) as f:
                owner = f.read().strip()
            if age < 2 and owner != "brightness":
                return False
    except Exception:
        pass
    with open(LOCK, "w") as f:
        f.write("brightness")
    return True

def on_brightness_change():
    if not acquire_lock():
        return
    pct = get_brightness()
    GLib.idle_add(lambda: webview.run_javascript(f"window.setBrightness({pct}, false)"))

def watcher():
    last = get_brightness()
    while True:
        time.sleep(0.2)
        cur = get_brightness()
        if cur != last:
            last = cur
            on_brightness_change()

threading.Thread(target=watcher, daemon=True).start()
Gtk.main()
