# 📜 Cursor Rules

## 1. General Project Structure
- Use clear, modular folder structures for backend (`app/`), frontend (`frontend/`), and device agent (`device-agent/`).
- All code should be well-documented and type-annotated where possible.

## 2. Backend (FastAPI)
- Use Pydantic models for all request/response validation.
- Use SQLAlchemy ORM for all database interactions.
- Use Alembic for database migrations; never edit tables manually in production.
- All endpoints must be versioned (e.g., `/api/v1/...`).
- Use dependency injection (`Depends`) for DB sessions, authentication, and permissions.
- Enforce RBAC (role-based access control) at the endpoint level.
- Use environment variables for secrets and DB credentials (never hardcode).
- Write reusable service functions for business logic (keep endpoints thin).
- Use JWT for authentication; tokens should be short-lived and securely signed.
- All errors must return clear, consistent JSON responses.

## 3. Frontend (React)
- Use functional components and hooks (no class components).
- Use TypeScript for type safety.
- Use a state management library (e.g., Redux Toolkit or Zustand) for global state.
- All API calls should be abstracted in a service layer (never call APIs directly in components).
- Use environment variables for API endpoints and secrets.
- Follow a consistent component and folder naming convention.
- Use React Router for navigation.
- All forms must have validation (e.g., using Formik + Yup).
- Use modern UI libraries (e.g., MUI, Ant Design) for consistency.

## 4. Database (MySQL)
- All schema changes must go through Alembic migrations.
- Use InnoDB tables and UTF-8 encoding.
- Use foreign keys for all relationships.
- Never store plaintext passwords or secrets.
- Use indexes on all foreign keys and frequently queried fields.

## 5. MQTT & Device Communication
- All device-server communication should use MQTT topics with a clear, hierarchical naming scheme (e.g., `tenant/{tenant_id}/device/{device_id}/status`).
- All MQTT messages must be JSON-encoded.
- Devices must buffer data locally (SQLite) when offline and sync when online.
- All device actions (watering, status, errors) must be logged and reported to the server.
- Use TLS for MQTT in production.

## 6. Raspberry Pi / IoT Agent
- Use Python 3 and type annotations.
- Use `paho-mqtt` for MQTT communication.
- Use `gpiozero` or `RPi.GPIO` for hardware control.
- All device logic must be resilient to power loss and network outages.
- Store all critical data locally (SQLite) and sync with the server when possible.
- Support OTA (over-the-air) updates in the future.

## 7. Testing & Quality
- All backend and frontend code must have unit and integration tests.
- Use pytest for Python, Jest for React.
- All code must pass linting and formatting checks (e.g., black, flake8, eslint, prettier).
- Use pre-commit hooks to enforce code quality.

## 8. Security
- Never log secrets or passwords.
- Use HTTPS for all web APIs.
- Use MQTT over TLS for device communication.
- Enforce strong password policies and account lockout on repeated failures.

## 9. Collaboration
- All changes must go through pull requests and code review.
- Write clear, descriptive commit messages.
- Update documentation and requirements as features evolve. 