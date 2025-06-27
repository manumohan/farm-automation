from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SectionBase(BaseModel):
    name: str
    section_code: str
    description: Optional[str] = None
    crop_type: Optional[str] = None
    area: float
    section_incharge_name: Optional[str] = None
    notes: Optional[str] = None

class SectionCreate(SectionBase):
    farm_id: int

class SectionUpdate(BaseModel):
    name: Optional[str] = None
    section_code: Optional[str] = None
    description: Optional[str] = None
    crop_type: Optional[str] = None
    area: Optional[float] = None
    section_incharge_name: Optional[str] = None
    notes: Optional[str] = None

class SectionOut(SectionBase):
    id: int
    farm_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    farm_name: Optional[str] = None  # For responses that include farm name
    
    class Config:
        from_attributes = True 