from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceCreate(BaseModel):
    farm_id: int
    device_uid: str
    status: Optional[str] = "offline"
    firmware_version: Optional[str] = None
    available_gpio_pins: Optional[str] = None

class DeviceOut(BaseModel):
    id: int
    farm_id: int
    device_uid: str
    status: str
    firmware_version: Optional[str] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    available_gpio_pins: Optional[str] = None
    is_deleted: bool

    class Config:
        from_attributes = True 