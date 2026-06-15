import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gdk, GLib
import subprocess, threading, time, socket

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
webview.load_uri("file:///home/drennant/navi-ui/syslog.html")
win.add(webview)
win.show_all()
win.input_shape_combine_region(__import__('cairo').Region())

def push(text):
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    GLib.idle_add(lambda: webview.run_javascript(f'window.pushLine("{text}")'))

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "0.0.0.0"

def get_uptime():
    with open('/proc/uptime') as f:
        secs = int(float(f.readline().split()[0]))
    h, m = secs // 3600, (secs % 3600) // 60
    return f"{h:02d}:{m:02d}"

def get_mem():
    with open('/proc/meminfo') as f:
        lines = {l.split(':')[0]: int(l.split()[1]) for l in f.readlines()[:3]}
    used = lines['MemTotal'] - lines['MemAvailable']
    pct = int(used / lines['MemTotal'] * 100)
    return pct

def get_cpu():
    out = subprocess.run(["bash", "-c", "grep 'cpu ' /proc/stat"], capture_output=True, text=True).stdout.split()
    idle = int(out[4])
    total = sum(int(x) for x in out[1:])
    return idle, total

hostname = socket.gethostname()
ip = get_ip()

push(f"NODE: {hostname}")
push(f"LINK: {ip}")
push("STATUS: CONNECTED")

last_idle, last_total = get_cpu()

def loop():
    global last_idle, last_total
    time.sleep(1)
    while True:
        uptime = get_uptime()
        mem = get_mem()
        idle, total = get_cpu()
        diff_idle = idle - last_idle
        diff_total = total - last_total
        cpu_pct = 100 - int(diff_idle / diff_total * 100) if diff_total > 0 else 0
        last_idle, last_total = idle, total

        push(f"UPTIME: {uptime}")
        push(f"CPU: {cpu_pct:02d}%  MEM: {mem:02d}%")
        time.sleep(4)

threading.Thread(target=loop, daemon=True).start()
Gtk.main()
