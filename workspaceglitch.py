import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import subprocess, threading

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
webview.load_uri("file:///home/drennant/navi-ui/workspaceglitch.html")
win.add(webview)
win.show_all()
win.input_shape_combine_region(__import__('cairo').Region())

def trigger():
    GLib.idle_add(lambda: webview.run_javascript("window.triggerGlitch()"))

def watcher():
    proc = subprocess.Popen(["socat", "-U", "-", f"UNIX-CONNECT:/run/user/1000/hypr/{__import__('os').environ['HYPRLAND_INSTANCE_SIGNATURE']}/.socket2.sock"], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        if line.startswith("workspace>>") or line.startswith("openwindow>>"):
            trigger()

threading.Thread(target=watcher, daemon=True).start()
Gtk.main()
