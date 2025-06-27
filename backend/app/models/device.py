from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    device_uid = Column(String(100), nullable=False)
    status = Column(String(50), default="offline")
    firmware_version = Column(String(50))
    last_seen = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)  # type: ignore
    available_gpio_pins = Column(String(255), nullable=True)  # Comma-separated pins 