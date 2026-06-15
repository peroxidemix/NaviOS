import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import subprocess, re, threading

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
webview.load_uri("file:///home/drennant/navi-ui/volumehud.html")
win.add(webview)
win.show_all()
win.input_shape_combine_region(__import__('cairo').Region())

def get_volume():
    out = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True).stdout
    m = re.search(r'(\d+)%', out)
    pct = int(m.group(1)) if m else 0
    mute_out = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True, text=True).stdout
    muted = "yes" in mute_out
    return pct, muted

import os, time as _t
LOCK = "/tmp/hud_lock"
def acquire_lock():
    try:
        if os.path.exists(LOCK):
            age = _t.time() - os.path.getmtime(LOCK)
            with open(LOCK) as f:
                owner = f.read().strip()
            if age < 2 and owner != "volume":
                return False
    except Exception:
        pass
    with open(LOCK, "w") as f:
        f.write("volume")
    return True

def on_volume_change():
    if not acquire_lock():
        return
    pct, muted = get_volume()
    GLib.idle_add(lambda: webview.run_javascript(f"window.setVolume({pct}, {'true' if muted else 'false'})"))

def watcher():
    proc = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        if "on sink #" in line and "change" in line:
            on_volume_change()

threading.Thread(target=watcher, daemon=True).start()
Gtk.main()
