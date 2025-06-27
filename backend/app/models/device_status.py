from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class DeviceStatus(Base):
    __tablename__ = "device_status"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    status = Column(String(50), nullable=False)  # online, offline, error, etc.
    message = Column(String(255))
    timestamp = Column(DateTime, server_default=func.now()) 