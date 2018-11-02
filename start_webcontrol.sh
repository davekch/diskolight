#!/bin/bash

# start pigpiod daemon if not already running
pgrep pigpiod > /dev/null || sudo pigpiod
sudo python3 webcontrol.py
