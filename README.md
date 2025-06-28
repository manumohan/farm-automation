# Farm Automation Platform

## 🎯 Project Overview
Build a multi-tenant farm automation platform that allows landlords/farmers to manage and automate irrigation across multiple farmlands. The system integrates with IoT devices (e.g. Raspberry Pi + relay boards) that control pumps and solenoid valves to water designated farm sections according to configured schedules.

## 🧑‍🌾 Key Actors
- **Super Admin** — Platform owner, can manage:
  - Tenants (create, disable, update)
  - Global settings
  - View all tenants' data & reports
  - Manage licensing & subscription
- **Tenant Admin (Landlord/Farmer)** — Owns one or more farmlands:
  - Configure farm settings, schedules, sections, and devices
  - Manage tenant users
  - View reports, activity logs, upcoming schedules
- **Tenant User (Farm Manager/Worker)** — Operates the farm:
  - View schedules
  - Manually run schedules
  - Check device status, receive notifications
  - Download/export reports
- **IoT Device (Raspberry Pi)** — Assigned to one farm:
  - Pull watering schedules
  - Execute watering according to schedule
  - Push reports and status to server
  - Run offline with SD card data
  - Support firmware updates pushed by the server

## 🧠 Functional Requirements
### ✅ Tenant/Farm Management
- Super admin can onboard new tenants.
- Tenant admins can register multiple farmlands.
- Each farmland can be subdivided into sections with different crops and water requirements.
- Attach an IoT device to each farm.

### ✅ Irrigation Schedules
- UI for tenant admin to:
  - Define schedules per farm section (e.g. Rubber Plantation = water 5 AM to 5:30 AM on M/W/F).
  - Configure water duration and frequency per section.
  - Set up global or seasonal irrigation patterns.

### ✅ IoT Device Integration
- Devices periodically pull updated schedules.
- Device can:
  - Activate water pump.
  - Sequentially open valves for each section.
  - Measure water flow and ensure it matches expectations.
- Offline mode:
  - Schedules can be loaded via SD card.
  - Device buffers reports and sensor data offline and uploads once internet is restored.

### ✅ Monitoring & Reporting
- Real-time dashboard:
  - Device status (online/offline)
  - Current/next scheduled runs
  - Alerts and notifications
- Historical reports per farm, per section:
  - Watering logs
  - Water flow rates
  - Sensor status
  - Exportable reports (CSV/PDF)

### ✅ Error Handling & Alerts
- Automatic notifications (email/SMS/push) for:
  - Device offline
  - Water flow anomalies (e.g. pump running but no water detected)
  - Valve or relay failure
- Automatic shutoff if water flow is not detected.
- Log errors and generate actionable reports.

### ✅ User Roles & Permissions
- Super admin can manage tenant admins.
- Tenant admin can add/remove tenant users.
- Granular permission options for tenant users (view-only vs. configure schedules).

## 🛠️ Non-Functional Requirements
- ✅ Scalability — Multi-tenant architecture with proper isolation of tenant data.
- ✅ Performance — Real-time device communication with minimal latency.
- ✅ Offline capability — Reliable offline functionality for IoT device.
- ✅ Security — Role-based authentication & authorization, encrypted device communications (MQTT over TLS), secure cloud APIs.
- ✅ Auditing — Every action (schedule changes, device status updates) logged with timestamp & actor.
- ✅ Maintainability — Clear, versioned APIs between device & server.
- ✅ Usability — Responsive web UI with intuitive farm/section setup wizards.

## ⚙️ Technical Considerations & Extras
- Communication Protocol — MQTT or HTTP long-polling between devices and server.
- Data Sync — Implement local data buffer (SQLite on the device) to cache reports.
- Flow Sensor — Connect to I/O pins to monitor water flow; shut off pump if no flow detected.
- Pump Safety Logic — Ensure pump cannot run if all valves are closed.
- Scheduling Engine — On-device scheduler that can gracefully recover if device reboots.
- Failover Mode — Default safe state if device cannot contact server.
- Push Notifications — Integrate with a notification service (e.g. Firebase, Twilio) for critical alerts.
- API Rate-Limiting — Prevent devices from spamming server if misconfigured.

## ✨ Future Enhancements (Nice to Have)
- Forecasting & AI — Predict irrigation needs using weather and soil moisture data.
- Mobile App — Native or PWA for quick farm status checks & manual overrides.
- Over-the-Air Updates — Push firmware updates to device remotely.
- Analytics — Water consumption trends, section-wise crop health monitoring.
- User-Specific Dashboards — Personalize dashboard per user role.

## 📋 Architectural Decisions & Preferences

### Authentication/Authorization
- Use custom JWT-based authentication for now (username & password login).
- Plan for future Google SSO integration.
- Device authentication will use tokens (not certificates).
- Web and device should support bidirectional communication.

### Deployment
- Local development only for now, but everything should be Dockerized.
- Support both on-premises and AWS cloud deployments in the future.

### Device Communication
- Devices may have low, unstable, or no internet.
- Use the most robust protocol for such environments (recommend MQTT as primary, with HTTP fallback if needed).

### Notifications
- Only email notifications for now, using a basic SMTP setup.

### Firmware Updates
- Backend will store and serve firmware binaries directly (no third-party service).

### User Management
- No self-registration; users are invited/managed by admins only.
- Admins should have robust user management capabilities.

## 🏗️ Tech Stack & MVP Plan

- **Backend:** FastAPI (Python)
- **API Style:** REST
- **Database:** MySQL (localhost:3088, user:root, password:root, db: farm_automation)
- **Frontend:** React (to be scaffolded after backend MVP)
- **Device Communication:** MQTT (offline-first, syncs when online)
- **Authentication:** JWT (username/password, admin-invite only)
- **Notifications:** Email via SMTP

### MVP Features
- User authentication (JWT, admin-invite flow)
- Tenant/farm/section CRUD
- Device registration and schedule assignment
- Basic schedule execution logic (backend only)
- Email notification setup (basic SMTP)
- Simple dashboard (device status, next run)

## 🚀 Local Development

To run the platform locally for rapid development:

### 1. Frontend (React)
- Navigate to the frontend directory:
  ```bash
  cd frontend
  npm install
  npm start
  ```
- The app will be available at [http://localhost:3000](http://localhost:3000)
- Uses the API URL set in `frontend/.env.development`

### 2. Backend (FastAPI)
- Navigate to the backend directory:
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- The API will be available at [http://localhost:8000](http://localhost:8000)
- **Note:** By default, the backend always loads environment variables from `backend/.env`. If you want to use `backend/.env.development`, you must manually copy or rename it to `.env` before running the backend locally:
  ```bash
  cp .env.development .env
  ```

### 3. MQTT Broker (Mosquitto)
- You can run Mosquitto locally (if installed) or via Docker:
  ```bash
  # Using Docker Compose (recommended)
  docker-compose -f docker/docker-compose.yml up mosquitto
  ```
- MQTT will be available at `mqtt://localhost:1883` (and WebSocket on 9001)

---

## 🐳 Running with Docker Compose

To run the full stack in Docker containers:

```bash
make up
# or
cd docker
docker-compose up --build
```

### Services Available
- **Frontend**: React app at [http://localhost:3000](http://localhost:3000)
- **Backend**: FastAPI at [http://localhost:8000](http://localhost:8000)
- **MQTT Broker**: Mosquitto at `mqtt://localhost:1883` and WebSocket at `ws://localhost:9001`
- **MQTT Management UI**: Custom web interface at [http://localhost:8088](http://localhost:8088)

### Environment Files Used
- **Backend**: Uses `backend/.env.development` (can be changed in `docker-compose.yml`)
- **Frontend**: Uses production build (reads from `frontend/.env.production` at build time)

## 🔧 MQTT Testing & Management

### MQTT Management UI
Access the MQTT management interface at [http://localhost:8088](http://localhost:8088) to:
- Monitor MQTT topics and messages
- Test device communications
- Debug MQTT connections
- View real-time message flow

### Testing MQTT Connections

#### 1. Using the Web UI
1. Open [http://localhost:8088](http://localhost:8088)
2. Use the embedded HiveMQ Web Client
3. Connect to:
   - **WebSocket**: `ws://localhost:9001`
   - **MQTT**: `localhost:1883`
4. Subscribe to test topics:
   - `test/topic`
   - `tenant/+/device/+/status`
   - `tenant/+/device/+/logs`

#### 2. Using Command Line
```bash
# Subscribe to a topic
docker exec -it mosquitto mosquitto_sub -h localhost -t "test/topic" -v

# Publish a message
docker exec -it mosquitto mosquitto_pub -h localhost -t "test/topic" -m "Hello from device agent"

# Test device status message
docker exec -it mosquitto mosquitto_pub -h localhost -t "tenant/1/device/123/status" -m '{"status": "online", "timestamp": "2024-01-01T12:00:00Z"}'
```

#### 3. Testing Device Agent Topics
```bash
# Device status updates
docker exec -it mosquitto mosquitto_pub -h localhost -t "tenant/1/device/123/status" -m '{"status": "online", "battery": 85, "signal": -45}'

# Device logs
docker exec -it mosquitto mosquitto_pub -h localhost -t "tenant/1/device/123/logs" -m '{"level": "info", "message": "Schedule executed successfully", "timestamp": "2024-01-01T12:00:00Z"}'

# Device events
docker exec -it mosquitto mosquitto_pub -h localhost -t "tenant/1/device/123/events" -m '{"event": "valve_opened", "section_id": 1, "duration": 300}'
```

### MQTT Topic Structure
The platform uses the following MQTT topic structure:
- `tenant/{tenant_id}/device/{device_id}/status` - Device status updates
- `tenant/{tenant_id}/device/{device_id}/logs` - Device logs
- `tenant/{tenant_id}/device/{device_id}/events` - Device events
- `tenant/{tenant_id}/device/{device_id}/commands` - Commands to device

### MQTT Configuration
- **Broker**: Mosquitto 2.0
- **Ports**: 1883 (MQTT), 9001 (WebSocket)
- **Authentication**: Anonymous access enabled
- **Persistence**: Enabled with data stored in `/mosquitto/data/`
- **Logging**: Enabled with logs in `/mosquitto/log/`
