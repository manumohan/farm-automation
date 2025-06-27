from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    peripheral_mapping_id = Column(Integer, ForeignKey("peripheral_mappings.id"), nullable=False)
    cron_expression = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 