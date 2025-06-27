from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # super_admin, tenant_admin, tenant_user
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationship to Tenant
    tenant = relationship("Tenant", back_populates="users") 