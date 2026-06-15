#!/bin/bash
FOCUSED=$(hyprctl activewindow -j | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['address'])")
echo $FOCUSED > /tmp/last_minimized
hyprctl dispatch movetoworkspacesilent special:scratch,address:$FOCUSED
