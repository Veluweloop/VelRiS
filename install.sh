#!/bin/bash

set -e

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="VELRIS"

AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/$APP_NAME.desktop"

VENV_DIR="$APP_DIR/.venv"

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------

info() {
    echo
    echo "==> $1"
}

error() {
    echo
    echo "ERROR: $1"
    exit 1
}

# ------------------------------------------------------------
# Check operating system
# ------------------------------------------------------------

info "Checking system"

if [ ! -f /etc/os-release ]; then
    error "/etc/os-release not found."
fi

. /etc/os-release

echo "Detected OS: $PRETTY_NAME"

# ------------------------------------------------------------
# Check required commands
# ------------------------------------------------------------

info "Checking required commands"

command -v python3 >/dev/null 2>&1 || error "python3 is not installed."
command -v pip3 >/dev/null 2>&1 || error "pip3 is not installed."
command -v firefox >/dev/null 2>&1 || error "Firefox is not installed."

# ------------------------------------------------------------
# Install system dependencies
# ------------------------------------------------------------

info "Installing system dependencies"

if command -v apt-get >/dev/null 2>&1; then

    sudo apt-get update

    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        firefox

else
    echo "apt-get not found."
    echo "Please install Python 3, venv, curl and Firefox manually."
fi

# ------------------------------------------------------------
# Create Python virtual environment
# ------------------------------------------------------------

info "Creating Python virtual environment"

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# ------------------------------------------------------------
# Update pip
# ------------------------------------------------------------

info "Updating pip"

"$VENV_DIR/bin/python" -m pip install --upgrade pip

# ------------------------------------------------------------
# Install Python dependencies
# ------------------------------------------------------------

if [ -f "$APP_DIR/requirements.txt" ]; then

    info "Installing Python dependencies"

    "$VENV_DIR/bin/pip" install \
        -r "$APP_DIR/requirements.txt"

else
    echo "No requirements.txt found."
fi

# ------------------------------------------------------------
# Make scripts executable
# ------------------------------------------------------------

info "Setting executable permissions"

chmod +x "$APP_DIR/start-kiosk.sh"
chmod +x "$APP_DIR/stop-kiosk.sh"
chmod +x "$APP_DIR/install.sh"

# ------------------------------------------------------------
# Create autostart directory
# ------------------------------------------------------------

info "Creating autostart directory"

mkdir -p "$AUTOSTART_DIR"

# ------------------------------------------------------------
# Create desktop autostart file
# ------------------------------------------------------------

info "Creating autostart entry"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Start kiosk application
Exec=$APP_DIR/start-kiosk.sh
Terminal=false
StartupNotify=false
X-GNOME-Autostart-enabled=true
EOF

echo
echo "Autostart file:"
echo "$DESKTOP_FILE"

# ------------------------------------------------------------
# Finish
# ------------------------------------------------------------

info "Installation complete"

echo
echo "Application directory:"
echo "  $APP_DIR"

echo
echo "Virtual environment:"
echo "  $VENV_DIR"

echo
echo "Autostart:"
echo "  $DESKTOP_FILE"

echo
echo "The kiosk will start automatically at the next graphical login."

echo
read -r -p "Restart the computer now? [y/N] " ANSWER

if [[ "$ANSWER" =~ ^[Yy]$ ]]; then
    echo "Restarting..."
    sudo reboot
fi