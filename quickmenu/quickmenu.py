import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import subprocess, json

class Api:
    def launch(self, label):
        if label == "switch":
            subprocess.Popen(["paplay", "--volume=65536", "/home/drennant/navi-ui/switch.wav"])
            return
        if label == "close" or not label:
            Gtk.main_quit()
            return
        subprocess.Popen(["paplay", "--volume=65536", "/home/drennant/navi-ui/open.wav"])
        cmd = {"terminal": "kitty", "browser": "firefox", "files": "thunar", "spotify": "spotify", "ryujinx": "flatpak run io.github.ryubing.Ryujinx", "bluetooth": "blueman-manager"}.get(label)
        if cmd:
            ws = subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True)
            wsid = json.loads(ws.stdout)["id"]
            subprocess.run(["hyprctl", "dispatch", "exec", f"[workspace {wsid}] {cmd}"])
        Gtk.main_quit()

api = Api()
win = Gtk.Window()
screen = win.get_screen()
visual = screen.get_rgba_visual()
if visual and screen.is_composited():
    win.set_visual(visual)
win.set_app_paintable(True)
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.EXCLUSIVE)
webview_settings_done=True

cm = WebKit2.UserContentManager()
def on_msg(cm, m):
    api.launch(m.to_string() if hasattr(m,'to_string') else m.get_js_value().to_string())
cm.connect("script-message-received::launch", on_msg)
cm.register_script_message_handler("launch")

webview = WebKit2.WebView.new_with_user_content_manager(cm)
webview.set_background_color(Gdk.RGBA(0,0,0,0))
webview.load_uri("file:///home/drennant/navi-ui/quickmenu/index.html")
win.add(webview)
win.show_all()
subprocess.Popen(["paplay", "--volume=65536", "/home/drennant/navi-ui/quickmenu/menu_open.wav"])
GLib.timeout_add(8000, Gtk.main_quit)
import os
def watch_pipe():
    try:
        fd = os.open("/tmp/quickmenu_pipe", os.O_RDONLY | os.O_NONBLOCK)
        os.read(fd, 10)
        os.close(fd)
    except Exception:
        pass
    webview.run_javascript("window.confirmSelection()")
    GLib.timeout_add(2800, Gtk.main_quit)
    return False
GLib.io_add_watch(os.open("/tmp/quickmenu_pipe", os.O_RDONLY | os.O_NONBLOCK), GLib.IO_IN, lambda *a: watch_pipe())
win.connect("destroy", Gtk.main_quit)
Gtk.main()
