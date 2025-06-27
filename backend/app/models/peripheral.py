from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class PeripheralType(Base):
    __tablename__ = "peripheral_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    scope = Column(String(20), nullable=False)  # 'section' or 'farm'
    exclusive_schedule = Column(Boolean, default=False, nullable=False)

class PeripheralMapping(Base):
    __tablename__ = "peripheral_mappings"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    peripheral_type_id = Column(Integer, ForeignKey("peripheral_types.id"), nullable=False)
    gpio_pin = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 