#!/bin/bash

echo "Starting in virtual enviroment"

cd /home/pixel/Documents/coding/Compressed-air-engine-python-part || { echo "Invalid directory"; exit 1; }

sudo ~/keyboard-env/bin/python core.py
