import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, WebKit2, GtkLayerShell, Gio, GLib
import subprocess
import json
import time
import threading

class Api:
    def launch(self, label):
        if label == "switch":
            subprocess.Popen(["paplay", "/home/drennant/navi-ui/switch.wav"])
            return
        if label == "open":
            subprocess.Popen(["paplay", "/home/drennant/navi-ui/open.wav"])
            return
        if label == "media-prev":
            subprocess.run(["playerctl", "previous"])
            return
        if label == "media-next":
            subprocess.run(["playerctl", "next"])
            return
        if label == "media-playpause":
            subprocess.run(["playerctl", "play-pause"])
            return
        if False: pass
        if label == "terminal":
            cmd, target = "kitty", "kitty"
        elif label == "browser":
            cmd, target = "firefox", "firefox"
        elif label == "files":
            cmd, target = "thunar", "thunar"
        elif label == "spotify":
            cmd, target = "spotify", "spotify"
        elif label == "ryujinx":
            cmd, target = "flatpak run io.github.ryubing.Ryujinx", "Ryujinx"
        elif label == "bluetooth":
            cmd, target = "blueman-manager", "blueman-manager"
        else:
            return

        ws = subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True)
        wsid = json.loads(ws.stdout)["id"]
        subprocess.Popen(["hyprctl", "dispatch", "exec", f"[workspace {wsid}] {cmd}"])

        def nudge():
            time.sleep(0.5)
            subprocess.run(["hyprctl", "dispatch", "movecursor", "1", "1"])
        threading.Thread(target=nudge, daemon=True).start()

api = Api()
win = Gtk.Window()
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.BACKGROUND)
for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM,
             GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
    GtkLayerShell.set_anchor(win, edge, True)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.ON_DEMAND)
content_manager = WebKit2.UserContentManager()
def on_message(content_manager, message):
    label = message.to_string() if hasattr(message, 'to_string') else message.get_js_value().to_string()
    api.launch(label)
content_manager.connect("script-message-received::launch", on_message)
content_manager.register_script_message_handler("launch")
webview = WebKit2.WebView.new_with_user_content_manager(content_manager)
webview.get_settings().set_property("media-playback-requires-user-gesture", False)
webview.load_uri("file:///home/drennant/navi-ui/index.html")
win.add(webview)
win.show_all()
subprocess.run(["pkill", "-f", "audio_watcher.sh"])
import time as _t; _t.sleep(0.3)
subprocess.run(["pkill", "-f", "paplay.*lainos"])
subprocess.Popen(["bash", "/home/drennant/navi-ui/audio_watcher.sh"])

def get_music_info():
    try:
        status = subprocess.run(["playerctl", "status"], capture_output=True, text=True, timeout=1).stdout.strip()
        if not status:
            return None
        title = subprocess.run(["playerctl", "metadata", "title"], capture_output=True, text=True, timeout=1).stdout.strip()
        artist = subprocess.run(["playerctl", "metadata", "artist"], capture_output=True, text=True, timeout=1).stdout.strip()
        art = subprocess.run(["playerctl", "metadata", "mpris:artUrl"], capture_output=True, text=True, timeout=1).stdout.strip()
        position = subprocess.run(["playerctl", "position"], capture_output=True, text=True, timeout=1).stdout.strip()
        length_us = subprocess.run(["playerctl", "metadata", "mpris:length"], capture_output=True, text=True, timeout=1).stdout.strip()
        progress = 0
        try:
            pos = float(position)
            length = float(length_us) / 1_000_000
            if length > 0:
                progress = int(pos / length * 100)
        except Exception:
            pass
        return {
            "title": title,
            "artist": artist,
            "art": art,
            "progress": progress,
            "playing": status == "Playing"
        }
    except Exception:
        return None

def music_loop():
    while True:
        info = get_music_info()
        if info:
            title = info["title"].replace('"', '\\"')
            artist = info["artist"].replace('"', '\\"')
            art = info["art"]
            js = f'updateMusic({{title:"{title}", artist:"{artist}", art:"{art}", progress:{info["progress"]}, playing:{"true" if info["playing"] else "false"}}})'
        else:
            js = 'updateMusic(null)'
        GLib.idle_add(lambda j=js: webview.run_javascript(j))
        time.sleep(1)

import time
threading.Thread(target=music_loop, daemon=True).start()

import socket as _socket
def get_ip():
    try:
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
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
    return int(used / lines['MemTotal'] * 100)

def get_cpu():
    out = subprocess.run(["bash", "-c", "grep 'cpu ' /proc/stat"], capture_output=True, text=True).stdout.split()
    idle = int(out[4])
    total = sum(int(x) for x in out[1:])
    return idle, total

def push_sys(text):
    text = text.replace("\\", "\\\\").replace('"', '\\"')
    webview.run_javascript(f'pushSysLine("{text}")')

def sys_loop():
    hostname = _socket.gethostname()
    ip = get_ip()
    GLib.idle_add(lambda: push_sys(f"NODE: {hostname}"))
    GLib.idle_add(lambda: push_sys(f"LINK: {ip}"))
    GLib.idle_add(lambda: push_sys("STATUS: CONNECTED"))
    last_idle, last_total = get_cpu()
    time.sleep(1)
    while True:
        uptime = get_uptime()
        mem = get_mem()
        idle, total = get_cpu()
        diff_idle = idle - last_idle
        diff_total = total - last_total
        cpu_pct = 100 - int(diff_idle / diff_total * 100) if diff_total > 0 else 0
        last_idle, last_total = idle, total
        GLib.idle_add(lambda u=uptime, c=cpu_pct, m=mem: push_sys(f"UP {u}  CPU {c:02d}%  MEM {m:02d}%"))
        time.sleep(4)

def start_sys_loop_when_ready(wv, event):
    if event == WebKit2.LoadEvent.FINISHED:
        threading.Thread(target=sys_loop, daemon=True).start()

webview.connect("load-changed", start_sys_loop_when_ready)
win.connect("destroy", Gtk.main_quit)
Gtk.main()
