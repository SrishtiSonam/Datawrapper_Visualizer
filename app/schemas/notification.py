from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Notification schema
class NotificationBase(BaseModel):
    message: str


class NotificationCreate(NotificationBase):
    student_id: int
    journal_id: int


class NotificationUpdate(BaseModel):
    is_read: bool = True


class Notification(NotificationBase):
    id: int
    student_id: int
    journal_id: int
    is_read: bool
    created_at: datetime

    class Config:
        orm_mode = True