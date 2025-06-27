from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class WateringLog(Base):
    __tablename__ = "watering_logs"
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    actual_water_amount = Column(Float)
    status = Column(String(50))
    error_message = Column(String(255))
    created_at = Column(DateTime, server_default=func.now()) 