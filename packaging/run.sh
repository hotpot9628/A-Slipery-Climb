#!/bin/sh
# Start A SLIPERY CLIMB from the folder this script lives in.
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE" || exit 1
chmod +x "./A Slipery Climb" 2>/dev/null
exec "./A Slipery Climb" "$@"
