#!/usr/bin/env bash
# Launch the static server, browser, and motion detector simultaneously.
# Press Ctrl-C (or let the script exit) and the trap kills all of them.
set -euo pipefail

# When this script exits for any reason, send a signal to every process in
# its process group (that's what `kill 0` does) — tears down all children.
trap 'kill 0' EXIT

# 1. Serve the starfield. Subshell so the `cd` doesn't affect the commands below.
( cd starfield && python3 -m http.server 8000 ) &

# 2. Give the server a moment to bind the port, then open the browser.
sleep 1
python3 open_browser.py &

# 3. Run the motion detector.
python3 index.py &

# Block here until Ctrl-C. Without `wait`, the script would reach the end,
# the EXIT trap would fire immediately, and everything would be killed at once.
wait
