#!/usr/bin/env bash
set -euo pipefail

source "$(dirname "$0")/venv/bin/activate"

trap 'kill 0' EXIT
( cd starfield && python3 -m http.server 8000 ) &
sleep 1

python3 open_browser.py &
python3 index.py & wait
