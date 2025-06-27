from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Farm(Base):
    __tablename__ = "farms"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    farm_code = Column(String(50), nullable=False)
    description = Column(String(500))
    location = Column(String(255))  # For coordinates
    total_area = Column(Float, nullable=False)  # in cents
    farm_owner_name = Column(String(255), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship to Tenant
    tenant = relationship("Tenant", back_populates="farms")
    
    # Relationship to Sections
    sections = relationship("Section", back_populates="farm") 