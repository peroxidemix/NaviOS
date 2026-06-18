import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import os, subprocess, json

HERE = os.path.dirname(os.path.abspath(__file__))

win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
             GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)
GtkLayerShell.set_exclusive_zone(win, -1)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.EXCLUSIVE)
screen = win.get_screen()
visual = screen.get_rgba_visual()
if visual and screen.is_composited():
    win.set_visual(visual)
win.set_app_paintable(True)

content_manager = WebKit2.UserContentManager()

def on_message(cm, message):
    data = json.loads(message.get_js_value().to_string())
    action = data.get('action')
    if action == 'list_dir':
        path = os.path.expanduser(data['path'])
        try:
            entries = []
            for name in sorted(os.listdir(path), key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower())):
                if name.startswith('.'):
                    continue
                full = os.path.join(path, name)
                entries.append({'name': name, 'path': full, 'is_dir': os.path.isdir(full)})
            result = {'ok': True, 'path': path, 'entries': entries, 'parent': os.path.dirname(path) if path != '/' else None}
        except Exception as e:
            result = {'ok': False, 'error': str(e)}
        js = f"window.onDirResult({json.dumps(result)})"
        GLib.idle_add(lambda: webview.run_javascript(js))
    elif action == 'open_file':
        subprocess.Popen(['xdg-open', data['path']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif action == 'sound':
        name = data.get('name','switch')
        wav = f'{HERE}/{name}.wav'
        print(f'playing {wav}')
        subprocess.Popen(['paplay', '--volume=65536', wav])
    elif action == 'quit':
        Gtk.main_quit()
    elif action == 'get_home':
        home = os.path.expanduser('~')
        GLib.idle_add(lambda: webview.run_javascript(f"window.onHome('{home}')"))

content_manager.connect('script-message-received::navi', on_message)
content_manager.register_script_message_handler('navi')

webview = WebKit2.WebView.new_with_user_content_manager(content_manager)
webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
webview.load_uri(f'file://{HERE}/filemanager.html')

win.add(webview)
win.show_all()
Gtk.main()
