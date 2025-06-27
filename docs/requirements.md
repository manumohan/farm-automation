# Farm Automation Platform — Detailed Requirements

## 1. Project Overview
Multi-tenant platform for landlords/farmers to manage and automate irrigation across multiple farmlands, integrating with IoT devices (Raspberry Pi + relay boards) for scheduled irrigation.

## 2. Key Actors
- Super Admin: Manages tenants, global settings, licensing, and can view all data.
- Tenant Admin: Manages farms, schedules, sections, devices, and users.
- Tenant User: Operates farm, runs schedules, checks status, receives notifications.
- IoT Device: Assigned to a farm, pulls schedules, executes irrigation, reports status, supports offline mode and firmware updates.

## 3. Functional Requirements
- Tenant/farm/section management (multi-tenant, sections with different crops/water needs)
- Device registration and assignment
- Irrigation scheduling (per section, duration, frequency, seasonal patterns)
- IoT device integration (pull schedules, activate pump/valves, measure/report water flow, offline mode, buffer data, upload when online)
- Monitoring & reporting (real-time dashboard, device status, logs, exportable reports)
- Error handling & alerts (email notifications for device offline, anomalies, failures, auto shutoff, error logs)
- User roles & permissions (admin-invite only, granular permissions)

## 4. Non-Functional Requirements
- Scalability, performance, offline capability, security (role-based auth, encrypted comms), auditing, maintainability, usability

## 5. Technical Decisions
- **Backend:** FastAPI (Python)
- **API:** REST
- **Database:** MySQL (localhost:3088, user:root, password:root, db: farm_automation)
- **Frontend:** React
- **Device Communication:** MQTT (offline-first, syncs when online)
- **Authentication:** JWT (username/password, admin-invite only)
- **Notifications:** Email via SMTP
- **Deployment:** Dockerized, supports local, on-prem, and AWS
- **Firmware:** Backend stores/serves binaries, no third-party
- **User Management:** No self-registration, admin-invite only

## 6. MVP Scope
- Auth (JWT, admin-invite)
- Tenant/farm/section CRUD
- Device registration & schedule assignment
- Basic schedule execution logic (backend)
- Email notification (SMTP)
- Simple dashboard (device status, next run)

## 7. Device/Offline Logic
- MQTT for device-server comms
- Device must work offline, buffer data, sync when online

## 8. Future Enhancements
- Google SSO, mobile app, analytics, AI/forecasting, OTA updates, user-specific dashboards 