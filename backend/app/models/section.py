from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    name = Column(String(255), nullable=False)
    section_code = Column(String(50), nullable=False)
    description = Column(String(500))
    crop_type = Column(String(100))
    area = Column(Float, nullable=False)  # in cents
    section_incharge_name = Column(String(255))  # optional
    notes = Column(String(1000))  # optional
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship to Farm
    farm = relationship("Farm", back_populates="sections") 