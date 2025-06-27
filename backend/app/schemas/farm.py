from pydantic import BaseModel
from typing import Optional

class FarmBase(BaseModel):
    name: str
    farm_code: str
    description: Optional[str] = None
    location: Optional[str] = None
    total_area: float
    farm_owner_name: str

class FarmCreate(FarmBase):
    tenant_id: Optional[int] = None  # Optional for super admin, required for tenant admin

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    farm_code: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    total_area: Optional[float] = None
    farm_owner_name: Optional[str] = None

class FarmOut(FarmBase):
    id: int
    tenant_id: int
    deleted: bool
    tenant_name: Optional[str] = None  # For super admin responses
    
    class Config:
        from_attributes = True 