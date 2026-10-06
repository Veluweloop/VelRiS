#!/bin/bash

set -u

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$APP_DIR/.venv"

WIFI_SSID="Veluweloop"
WIFI_PASSWORD="Veluwelopen01"

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
# Connect to Wi-Fi
# ------------------------------------------------------------

echo "Checking Wi-Fi connection..."

if ! command -v nmcli >/dev/null 2>&1; then
    echo "ERROR: nmcli is not installed."
    exit 1
fi

# Check current connection
CURRENT_WIFI=$(nmcli -t -f ACTIVE,SSID dev wifi | grep '^yes:' | cut -d: -f2- || true)

if [ "$CURRENT_WIFI" = "$WIFI_SSID" ]; then
    echo "Already connected to Wi-Fi: $WIFI_SSID"
else
    echo "Connecting to Wi-Fi: $WIFI_SSID..."

    nmcli device wifi connect "$WIFI_SSID" password "$WIFI_PASSWORD"

    if [ $? -ne 0 ]; then
        echo "ERROR: Could not connect to Wi-Fi."
        exit 1
    fi
fi

echo "Waiting for network..."

MAX_WIFI_ATTEMPTS=30
WIFI_ATTEMPT=0

while ! nmcli networking connectivity check 2>/dev/null | grep -qE 'full|limited'; do
    WIFI_ATTEMPT=$((WIFI_ATTEMPT + 1))

    if [ "$WIFI_ATTEMPT" -ge "$MAX_WIFI_ATTEMPTS" ]; then
        echo "ERROR: Network did not become available."
        exit 1
    fi

    sleep 1
done

echo "Network is available."

# ------------------------------------------------------------
# Update application from Git
# ------------------------------------------------------------

echo "Updating application from Git..."

cd "$APP_DIR" || {
    echo "ERROR: Could not enter application directory."
    exit 1
}

# Make sure this is a Git repository
if [ ! -d "$APP_DIR/.git" ]; then
    echo "ERROR: $APP_DIR is not a Git repository."
    exit 1
fi

# Fetch latest changes
git fetch origin

# Check whether local branch is behind
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "@{u}" 2>/dev/null || true)

if [ -z "$REMOTE" ]; then
    echo "WARNING: No upstream branch configured."
else
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo "Application is already up to date."
    else
        echo "New version available."
        echo "Pulling latest changes..."

        git pull --ff-only

        if [ $? -ne 0 ]; then
            echo "ERROR: Git pull failed."
            exit 1
        fi

        echo "Git update completed."
    fi
fi

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