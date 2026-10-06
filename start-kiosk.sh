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
# Wi-Fi Configuration
# ------------------------------------------------------------

WIFI_SSID="Veluweloop"
WIFI_PASSWORD="Veluwelopen01"

# How long to wait for Wi-Fi to become available
WIFI_MAX_ATTEMPTS=30

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

echo "Checking Wi-Fi..."

if ! command -v nmcli >/dev/null 2>&1; then
    echo "WARNING: nmcli is not installed."
    echo "Continuing without Wi-Fi."
else

    WIFI_CONNECTED=false

    # First check if already connected to the requested Wi-Fi
    CURRENT_WIFI=$(nmcli -t -f ACTIVE,SSID dev wifi 2>/dev/null \
        | grep '^yes:' \
        | cut -d: -f2- || true)

    if [ "$CURRENT_WIFI" = "$WIFI_SSID" ]; then
        echo "Already connected to Wi-Fi: $WIFI_SSID"
        WIFI_CONNECTED=true
    else
        echo "Wi-Fi is not currently connected to $WIFI_SSID."

        # Give the Wi-Fi adapter some time to initialize
        for ((i=1; i<=WIFI_MAX_ATTEMPTS; i++)); do

            echo "Wi-Fi attempt $i/$WIFI_MAX_ATTEMPTS..."

            # Refresh the Wi-Fi scan
            nmcli device wifi rescan >/dev/null 2>&1 || true

            # Check whether our SSID is visible
            if nmcli -t -f SSID device wifi list 2>/dev/null \
                | grep -Fxq "$WIFI_SSID"; then

                echo "Found Wi-Fi network: $WIFI_SSID"
                break
            fi

            if [ "$i" -eq "$WIFI_MAX_ATTEMPTS" ]; then
                echo "WARNING: Wi-Fi network '$WIFI_SSID' was not found."
                echo "Continuing without Wi-Fi."
                break
            fi

            sleep 2
        done

        # Try connecting if the network was found
        if nmcli -t -f SSID device wifi list 2>/dev/null \
            | grep -Fxq "$WIFI_SSID"; then

            echo "Connecting to Wi-Fi: $WIFI_SSID..."

            if nmcli device wifi connect "$WIFI_SSID" \
                password "$WIFI_PASSWORD"; then

                echo "Wi-Fi connection successful."
                WIFI_CONNECTED=true

            else
                echo "WARNING: Could not connect to Wi-Fi."
                echo "Continuing without Wi-Fi."
            fi
        fi
    fi

    if [ "$WIFI_CONNECTED" = true ]; then
        echo "Wi-Fi is available."

        # Give NetworkManager a moment to establish Internet access
        echo "Checking Internet connectivity..."

        for ((i=1; i<=10; i++)); do
            CONNECTIVITY=$(nmcli networking connectivity check 2>/dev/null || true)

            if [ "$CONNECTIVITY" = "full" ]; then
                echo "Internet connection is available."
                break
            fi

            echo "Waiting for Internet connection ($i/10)..."
            sleep 1
        done

        CONNECTIVITY=$(nmcli networking connectivity check 2>/dev/null || true)

        if [ "$CONNECTIVITY" != "full" ]; then
            echo "WARNING: Wi-Fi is connected, but Internet is not available."
        fi
    fi
fi

# ------------------------------------------------------------
# Update application from Git
# ------------------------------------------------------------

echo "Checking for application updates..."

cd "$APP_DIR" || {
    echo "ERROR: Could not enter application directory."
    exit 1
}

if [ ! -d "$APP_DIR/.git" ]; then

    echo "WARNING: $APP_DIR is not a Git repository."
    echo "Skipping Git update."

else

    # Only attempt Git operations if Internet is available
    INTERNET_AVAILABLE=false

    if command -v curl >/dev/null 2>&1; then
        if curl --silent --head --max-time 5 https://github.com \
            >/dev/null 2>&1; then
            INTERNET_AVAILABLE=true
        fi
    fi

    if [ "$INTERNET_AVAILABLE" = true ]; then

        echo "Internet is available."
        echo "Updating application from Git..."

        # Get latest information from remote
        if git fetch origin; then

            # Determine the remote branch
            REMOTE_BRANCH=$(git symbolic-ref --short --quiet '@{u}' 2>/dev/null || true)

            if [ -z "$REMOTE_BRANCH" ]; then
                echo "WARNING: No upstream branch configured."
                echo "Skipping Git update."
            else

                echo "Remote branch: $REMOTE_BRANCH"

                # Remove the "origin/" prefix
                REMOTE_REF="origin/${REMOTE_BRANCH#*/}"

                echo "Discarding local changes..."
                git reset --hard "$REMOTE_REF"

                if [ $? -ne 0 ]; then
                    echo "ERROR: Could not reset repository."
                    exit 1
                fi

                echo "Removing untracked files..."
                git clean -fd

                if [ $? -ne 0 ]; then
                    echo "ERROR: Could not clean repository."
                    exit 1
                fi

                echo "Application successfully updated from Git."

            fi

        else

            echo "WARNING: Git fetch failed."
            echo "Continuing with existing application."

        fi

    else

        echo "WARNING: Internet is not available."
        echo "Skipping Git update."
        echo "Starting the existing local application."

    fi
fi

echo "Checking script permissions..."

find "$APP_DIR" -maxdepth 1 -type f -name "*.sh" -exec chmod +x {} \;

echo "Shell scripts are executable."

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
# Check Firefox
# ------------------------------------------------------------

echo "Checking Firefox..."

if pgrep -x firefox >/dev/null 2>&1; then

    echo "Firefox is already running."

else

    echo "No existing Firefox process."

    # --------------------------------------------------------
    # Start Firefox kiosk
    # --------------------------------------------------------

    echo "Starting Firefox kiosk..."

    firefox \
        --kiosk \
        "$URL" \
        >/dev/null 2>&1 &

    FIREFOX_PID=$!

    echo "Firefox PID: $FIREFOX_PID"

fi

# ------------------------------------------------------------
# Startup complete
# ------------------------------------------------------------

echo "Kiosk startup complete."
echo "Startup finished: $(date)"

exit 0