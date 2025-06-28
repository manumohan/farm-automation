# Device Agent (Raspberry Pi) TODO

## Next Steps for Development

- [ ] **Config Management**
  - Implement secure loading of `device_config.json` (read-only, device identity, secrets)
  - Implement editable `metadata_config.json` (operational settings, sync toggles)
  - Ensure configs/logs are stored outside codebase (e.g., `/data/`)

- [ ] **MQTT Communication**
  - Implement robust MQTT client (paho-mqtt)
  - Handle offline/online sync and buffering
  - Use topic structure: `tenant/{tenant_id}/device/{device_id}/status`
  - Ensure all messages are JSON

- [ ] **Schedule Execution**
  - Parse and execute watering schedules from backend
  - Implement local schedule fallback (from config or SQLite)
  - Add safety checks (e.g., pump/valve logic, flow sensor integration)

- [ ] **Local Storage & Sync**
  - Use SQLite for local logs/events
  - Implement data sync logic with backend
  - Add toggle for data sync in config

- [ ] **Logging & Error Handling**
  - Implement robust logging (local and remote)
  - Handle and report errors (network, hardware, schedule)

- [ ] **OTA Updates (Planned)**
  - Design for future over-the-air update support

- [ ] **Documentation**
  - Update `SETUP.md` and `REQUIREMENTS.md` as features are implemented

---

> For more details, see `device-agent/REQUIREMENTS.md` and `SETUP.md`. 