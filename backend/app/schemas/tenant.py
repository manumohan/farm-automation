from pydantic import BaseModel
from typing import Optional

class TenantBase(BaseModel):
    name: str
    description: Optional[str] = None
    active: bool

class TenantCreate(TenantBase):
    pass

class TenantRead(TenantBase):
    id: int

    class Config:
        orm_mode = True 