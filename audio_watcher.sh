#!/bin/bash

( while true; do paplay ~/navi-ui/lainos.mp3; sleep 0.5; done ) &disown

LAST_COUNT=-1
while true; do
    python3 - << 'PYEOF'
import subprocess, json, time

clients = json.loads(subprocess.run(["hyprctl", "clients", "-j"], capture_output=True, text=True).stdout)
active_ws = json.loads(subprocess.run(["hyprctl", "activeworkspace", "-j"], capture_output=True, text=True).stdout)["id"]
count = len([c for c in clients if c.get("workspace", {}).get("id") == active_ws and c.get("class","") not in ("filemanager.py",)])

inputs = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True).stdout
blocks = inputs.split("Sink Input #")
ids = []
for b in blocks[1:]:
    if "application.name = \"paplay\"" in b and "lainos.mp3" in b:
        ids.append(b.split("\n")[0].strip())

music_status = subprocess.run(["playerctl", "status"], capture_output=True, text=True).stdout.strip()
music_playing = (music_status == "Playing")
state = "muted" if (count > 0 or music_playing) else "playing"

with open("/tmp/audio_state", "a+") as f:
    f.seek(0)
    last = f.read().strip()
    if state != last:
        for sid in ids:
            rng = range(100, -10, -10) if state == "muted" else range(0, 110, 10)
            for v in rng:
                v = max(0, min(100, v))
                subprocess.run(["pactl", "set-sink-input-volume", sid, f"{v}%"])
                time.sleep(0.03)
        f.seek(0); f.truncate(); f.write(state)
    else:
        target_vol = "0%" if state == "muted" else "100%"
        for sid in ids:
            subprocess.run(["pactl", "set-sink-input-volume", sid, target_vol])
PYEOF
    sleep 1
done
