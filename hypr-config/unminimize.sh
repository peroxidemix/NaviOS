#!/bin/bash
LAST=$(cat /tmp/last_minimized)
hyprctl dispatch movetoworkspace 1,address:$LAST
