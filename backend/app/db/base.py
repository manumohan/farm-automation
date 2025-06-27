from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models for Alembic autogenerate
from app.models import tenant, user, farm, section, device, schedule, watering_log, device_status 