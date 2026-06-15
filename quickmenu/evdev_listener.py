import evdev
from evdev import ecodes
import subprocess

KEYBOARD = "/dev/input/event2"
RIGHTSHIFT = ecodes.KEY_RIGHTSHIFT

dev = evdev.InputDevice(KEYBOARD)

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY and event.code == RIGHTSHIFT:
        if event.value == 1:  # press
            subprocess.run(["pkill", "-f", "quickmenu.py"]); subprocess.Popen(["python3", "/home/drennant/navi-ui/quickmenu/quickmenu.py"])
        elif event.value == 0:  # release
            with open("/tmp/quickmenu_pipe", "w") as f:
                f.write("go\n")
