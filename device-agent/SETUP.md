# Raspberry Pi Device Agent Setup Guide

This guide documents all steps, dependencies, and configuration needed to run the device agent natively (without Docker) on a Raspberry Pi.

---

## 1. System Requirements
- Raspberry Pi (any model, recommended: Pi 3 or newer)
- Raspberry Pi OS (Debian-based)
- Python 3.7+
- Network access (WiFi or Ethernet)

---

## 2. System Package Installation
Run these commands on your Pi:

```sh
sudo apt update
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-rpi.gpio sqlite3 -y
```

---

## 3. Python Dependencies
Install Python packages from `requirements.txt`:

```sh
cd ~/path/to/device-agent
pip3 install -r requirements.txt
```

---

## 4. Configuration
- Place your `device_config.json` and `metadata_config.json` in `/data/` or another persistent directory outside the codebase.
- Ensure the agent has read/write permissions to `/data/`.

---

## 5. Running the Agent
Run the agent manually:

```sh
python3 agent.py
```

---

## 6. (Optional) Auto-Start on Boot
To run the agent automatically on boot, set up a systemd service. Example:

```ini
# /etc/systemd/system/device-agent.service
[Unit]
Description=Farm Automation Device Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/device-agent/agent.py
WorkingDirectory=/home/pi/device-agent
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```sh
sudo systemctl daemon-reload
sudo systemctl enable device-agent
sudo systemctl start device-agent
```

---

## 7. Additional Notes
- Enable SSH for remote management: `sudo raspi-config`
- Keep this file updated with any new dependencies or setup steps as the project evolves. 