from pydantic import BaseModel
from typing import Optional

class ScheduleBase(BaseModel):
    cron_expression: str
    duration_minutes: int

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    cron_expression: Optional[str]
    duration_minutes: Optional[int]

class ScheduleOut(ScheduleBase):
    id: int
    peripheral_mapping_id: int
    is_deleted: bool
    class Config:
        orm_mode = True 