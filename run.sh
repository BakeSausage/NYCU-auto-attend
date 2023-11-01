#!/bin/bash

cd "$(dirname "$0")"

if [ ! -f "config.ini" ]; then
    pip install -r requirements.txt
fi

python auto-attend.py

read -p "Press Enter to exit"