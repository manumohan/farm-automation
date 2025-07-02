#!/bin/bash
set -e

# Usage: bash build_deb.sh [version]
version="${1:-1.0.0}"
pkg_name="device-agent"
build_dir="${pkg_name}_build"
dist_dir="dist"
maintainer="Your Name <you@example.com>"

# Clean up previous builds
rm -rf "$build_dir" "$dist_dir"
mkdir -p "$build_dir/DEBIAN"
mkdir -p "$build_dir/usr/local/bin"
mkdir -p "$build_dir/opt/device-agent"
mkdir -p "$build_dir/etc/device-agent"
mkdir -p "$build_dir/lib/systemd/system"
mkdir -p "$dist_dir"

# Create control file
cat > "$build_dir/DEBIAN/control" <<EOF
Package: $pkg_name
Version: $version
Section: base
Priority: optional
Architecture: all
Depends: python3, python3-pip
Maintainer: $maintainer
Description: IoT device agent for farm automation
EOF

# Copy agent code
cp -r agent.py mqtt_hello.py requirements.txt "$build_dir/opt/device-agent/"

# Config template (always include as example)
cat > "$build_dir/etc/device-agent/config.json.example" <<EOF
{
  "deviceId": "REPLACE_WITH_DEVICE_ID",
  "farmId": "REPLACE_WITH_FARM_ID",
  "mqtt_broker": "REPLACE_WITH_BROKER",
  "mqtt_port": 1883
}
EOF

# Remove any real config from the package (if present)
rm -f "$build_dir/etc/device-agent/config.json"

# Wrapper script
cat > "$build_dir/usr/local/bin/device-agent" <<EOF
#!/bin/bash
exec /opt/device-agent/venv/bin/python /opt/device-agent/agent.py --config /etc/device-agent/config.json
EOF
chmod +x "$build_dir/usr/local/bin/device-agent"

# Systemd service
cat > "$build_dir/lib/systemd/system/device-agent.service" <<EOF
[Unit]
Description=Farm Automation Device Agent
After=network.target

[Service]
ExecStart=/usr/local/bin/device-agent
Restart=always
User=root
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Post-install script to set up venv, install dependencies, and enable/start the service
cat > "$build_dir/DEBIAN/postinst" <<EOF
#!/bin/bash
set -e
if [ ! -d /opt/device-agent/venv ]; then
  python3 -m venv /opt/device-agent/venv
fi
/opt/device-agent/venv/bin/pip install --upgrade pip
/opt/device-agent/venv/bin/pip install -r /opt/device-agent/requirements.txt
# Only create config if it does not exist
if [ ! -f /etc/device-agent/config.json ]; then
  cp /etc/device-agent/config.json.example /etc/device-agent/config.json
  echo "Created default config at /etc/device-agent/config.json. Please edit this file with your device settings."
fi
systemctl daemon-reload
systemctl enable device-agent.service
systemctl restart device-agent.service
EOF
chmod 755 "$build_dir/DEBIAN/postinst"

# Build the .deb
dpkg-deb --build "$build_dir" "$dist_dir/${pkg_name}_${version}.deb"
echo "\nDEB package created at $dist_dir/${pkg_name}_${version}.deb" 