#!/bin/bash

set -u

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"

PYTHON="$VENV_DIR/bin/python"
APP="$APP_DIR/main.py"

HOST="127.0.0.1"
PORT="5000"
URL="http://${HOST}:${PORT}/"

LOG_DIR="$APP_DIR/logs"
APP_LOG="$LOG_DIR/app.log"
START_LOG="$LOG_DIR/startup.log"

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

mkdir -p "$LOG_DIR"

exec >> "$START_LOG" 2>&1

echo
echo "============================================================"
echo "Kiosk startup: $(date)"
echo "Application directory: $APP_DIR"
echo "============================================================"

# ------------------------------------------------------------
# Basic checks
# ------------------------------------------------------------

if [ ! -x "$PYTHON" ]; then
    echo "ERROR: Python virtual environment not found:"
    echo "$PYTHON"
    exit 1
fi

if [ ! -f "$APP" ]; then
    echo "ERROR: Application not found:"
    echo "$APP"
    exit 1
fi

# ------------------------------------------------------------
# Prevent duplicate application instances
# ------------------------------------------------------------

if pgrep -f "$APP" >/dev/null 2>&1; then
    echo "Application is already running."
else
    echo "Starting Python application..."

    nohup "$PYTHON" "$APP" >> "$APP_LOG" 2>&1 &
    APP_PID=$!

    echo "Python PID: $APP_PID"
fi

# ------------------------------------------------------------
# Wait for the web application
# ------------------------------------------------------------

echo "Waiting for application at $URL ..."

MAX_ATTEMPTS=60
ATTEMPT=0

while ! curl --silent --output /dev/null --fail "$URL"; do
    ATTEMPT=$((ATTEMPT + 1))

    if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
        echo "ERROR: Application did not become ready."
        echo "Check:"
        echo "$APP_LOG"
        exit 1
    fi

    sleep 1
done

echo "Application is ready."

# ------------------------------------------------------------
# Close any existing Firefox instance
# ------------------------------------------------------------

echo "Checking Firefox..."

if pgrep -x firefox >/dev/null 2>&1; then
    echo "Firefox is already running."

    # Don't forcibly kill an existing user's Firefox session.
    # Firefox may already be using the profile we need.
else
    echo "No existing Firefox process."
fi

# ------------------------------------------------------------
# Start Firefox kiosk
# ------------------------------------------------------------

echo "Starting Firefox kiosk..."

firefox \
    --kiosk \
    "$URL" \
    >/dev/null 2>&1 &

FIREFOX_PID=$!

echo "Firefox PID: $FIREFOX_PID"
echo "Kiosk startup complete."

exit 0