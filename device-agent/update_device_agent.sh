#!/bin/bash

set -e

# Configurable URL for the latest .deb package
DEB_URL="https://github.com/yourorg/device-agent/releases/latest/download/device-agent-latest.deb"
DEB_FILE="/tmp/device-agent-latest.deb"
SERVICE_NAME="device-agent.service"

# Download the latest .deb
echo "Downloading latest device-agent package..."
curl -L -o "$DEB_FILE" "$DEB_URL"

# Install or upgrade the package
echo "Installing device-agent package..."
sudo dpkg -i "$DEB_FILE"

# Fix missing dependencies if any
sudo apt-get install -f -y

# Restart the device-agent service
if systemctl list-units --full -all | grep -Fq "$SERVICE_NAME"; then
    echo "Restarting $SERVICE_NAME..."
    sudo systemctl restart "$SERVICE_NAME"
    echo "$SERVICE_NAME restarted."
else
    echo "Warning: $SERVICE_NAME not found. Please start the agent manually if needed."
fi

echo "Update complete." 