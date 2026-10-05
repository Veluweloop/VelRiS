#!/bin/bash

set -u

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$APP_DIR/main.py"

echo "Stopping kiosk application..."

# Stop the Python application started from this repository.
pkill -f "$APP" 2>/dev/null || true

echo "Stopping Firefox..."

# Only do this if this machine is dedicated to the kiosk.
pkill -x firefox 2>/dev/null || true

echo "Kiosk stopped."