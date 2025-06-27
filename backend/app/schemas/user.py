from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str
    status: Optional[str] = "active"
    tenant_id: Optional[int] = None  # None for super_admin
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    deleted: bool
    tenant_name: Optional[str] = None  # For super admin responses
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[str] = None
    tenant_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None 