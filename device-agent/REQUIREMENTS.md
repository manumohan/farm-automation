# Device Agent (Raspberry Pi) – Requirements & Architecture Reference

## 1. Device Identity & Secure Config
- **Device ID:** Use a UUID or user-defined ID, saved in a secure config file (e.g., `/data/device_config.json`).
- **Secure Config JSON:**
  - Contains only non-changeable, secure items:
    - `device_id`
    - MQTT credentials (username, password, broker, port, TLS info)
    - (Optionally) API endpoint, device secret/token
  - **Location:** Outside the codebase, e.g., `/data/device_config.json`
  - **Editable only for provisioning** (not by end user in normal operation).

## 2. Metadata Config (Operational Settings)
- **Metadata JSON:**
  - Contains all operational and changeable metadata:
    - Schedules
    - Pin mappings
    - Farm assignment
    - Peripheral configuration
    - Any other runtime settings
    - **Data sync toggle** (e.g., `"data_sync_enabled": true/false`)
  - **Location:** Outside the codebase, e.g., `/data/metadata_config.json`
  - **Editable by user/admin for offline/manual operation.**
  - If both config files are present, Pi should function fully offline.

## 3. Data Storage
- **SQLite DB:**
  - Store all logs, events, and unsynced data.
  - Mark data as synced after successful push to server.
  - Store in `/data/` or similar, not in code directory.

## 4. MQTT Communication
- **Topics:** Device subscribes to its own topic for commands/config updates. Publishes status, logs, and sensor data.
- **Status:** Device sends heartbeat/status every 30 seconds (or configurable). Web UI shows device as "active" if status received recently.

## 5. Schedule Execution & Safety Logic
- **Schedule runner:** Executes actions based on metadata config (valve, pump, etc.). Checks for exclusivity. Logs all actions and errors.
- **Safety checks:** Confirm flow sensor after pump/valve activation. Force kill if valve open > 1 hour. On power loss/reboot, log event and resume/cleanup as needed. Always turn off pump before valve at end of schedule. Log all state changes and errors.

## 6. Sync & Offline Mode
- **Sync logic:**
  - If `data_sync_enabled` is true and internet is available: Push unsynced logs/events to server, mark as synced, and delete from SQLite.
  - If `data_sync_enabled` is false, never push data (privacy mode).
- **Manual override:** If offline, allow manual config update via JSON.

## 7. OTA Software Updates
- **Update flow:** Web UI triggers update (pushes new code or signals device to pull update). Device downloads and applies update, but keeps `/data/` and config untouched. Rollback on failure.

## 8. Extensibility & Monitoring
- **Future sensors:** Design for easy addition of new sensors (amp/voltage, etc.).
- **Remote diagnostics:** Allow remote log dump or debug info via MQTT/command.
- **Security:** Secure MQTT (TLS, per-device credentials). Secure config and data storage (permissions, no secrets in logs).

## 9. Logging & Audit
- **Comprehensive logging:** All actions, errors, state changes, and sync events. Logs stored in SQLite and optionally in a rotating file for local review.

---

## Additional Best-Practice Suggestions
- **Watchdog/Healthcheck:** Use a watchdog timer or systemd service to auto-restart agent if it crashes.
- **Graceful shutdown:** Handle SIGTERM/SIGINT to safely close valves/pumps and log shutdown.
- **Configurable intervals:** Make status update and sync intervals configurable.
- **Unit tests:** Include tests for schedule logic, safety checks, and sync.
- **Comprehensive error handling:** All exceptions and failures should be logged and, if possible, reported to the backend.
- **Rotating log files:** Optionally keep a local log file with rotation for troubleshooting.
- **Remote diagnostics:** Allow remote triggering of log dumps or status reports for support/debugging.
- **File/folder permissions:** Ensure `/data/` and config files are only readable/writable by the agent user.

---

## Directory Structure Example
```
/data/
  device_config.json      # Secure, non-changeable (device_id, MQTT creds, etc)
  metadata_config.json    # Schedules, pin mappings, farm assignment, data_sync_enabled, etc
  device_logs.db          # SQLite logs/events
  (other runtime files)
```

---

## Summary Table
| File                  | Contents (examples)                                  | Editable?         | Purpose                |
|-----------------------|------------------------------------------------------|-------------------|------------------------|
| device_config.json    | device_id, MQTT creds, device secret                 | Provision only    | Identity, security     |
| metadata_config.json  | schedules, pin mapping, farm_id, data_sync_enabled   | Yes (admin/user)  | Runtime operation      |
| device_logs.db        | logs, events, sync status                            | Internal only     | Logging, audit, sync   |

---

**Reference this file in all device agent code and documentation for requirements and architecture decisions.** 