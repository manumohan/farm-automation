# Device Agent Installer (v1.0.2)

This guide explains how to build the device agent `.deb` package, copy it to your Raspberry Pi, install it, and configure it for your environment.

---

## Important Note About Configuration

- The package only includes a config template as `/etc/device-agent/config.json.example`.
- On **first install**, the template is copied to `/etc/device-agent/config.json` **if it does not already exist**.
- On **upgrades or reinstalls**, your existing `/etc/device-agent/config.json` is **preserved and will NOT be overwritten**.
- Edit your config as needed and it will be kept safe across updates.

---

## 1. Build the .deb Package

On your development machine (Mac/Linux):

```bash
cd device-agent
bash build_deb.sh
```

The package will be created at:
```
dist/device-agent_1.0.2.deb
```

---

## 2. Copy the .deb to Your Raspberry Pi

Replace `<pi-user>` and `<pi-host>` with your Pi's username and hostname or IP:

```bash
scp dist/device-agent_1.0.2.deb <pi-user>@<pi-host>:/tmp/
```

Example:
```bash
scp dist/device-agent_1.0.2.deb manu@raspberrypi.local:/tmp/
```

---

## 3. Install the Package on the Pi

SSH into your Pi:
```bash
ssh <pi-user>@<pi-host>
```

Then install the package:
```bash
sudo dpkg -i /tmp/device-agent_1.0.2.deb
sudo apt-get install -f -y
```

---

## 4. Configure the Device Agent

The config file is located at:
```
/etc/device-agent/config.json
```

Edit it with:
```bash
sudo nano /etc/device-agent/config.json
```

Example config:
```json
{
  "deviceId": "YOUR_DEVICE_ID",
  "farmId": "YOUR_FARM_ID",
  "mqtt_broker": "YOUR_MQTT_BROKER_ADDRESS",
  "mqtt_port": 1883
}
```
- `deviceId`: The unique ID for this device (must match your backend).
- `farmId`: The farm this device belongs to (required for status updates; ask your admin if unsure).
- `mqtt_broker`: The IP or hostname of your MQTT broker (e.g., `192.168.1.49` or `mosquitto`).
- `mqtt_port`: Usually `1883` for non-TLS.

**Note:** The config file will NOT be overwritten on reinstall or upgrade. Your settings are safe.

---

## 5. Start/Restart the Agent

After editing the config, restart the agent:
```bash
sudo systemctl restart device-agent
```

Check the status:
```bash
sudo systemctl status device-agent
```

---

## 6. View Logs (Optional)

To see real-time logs:
```bash
journalctl -u device-agent -f
```

---

## Troubleshooting
- Ensure the config file is valid JSON and readable by the agent.
- The agent must be able to reach the MQTT broker on the specified address and port.
- If you change the config, always restart the agent.

---

For further help, see the main project documentation or contact the maintainer. 