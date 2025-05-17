from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.user import User

# Attachment schema
class AttachmentBase(BaseModel):
    attachment_type: str = Field(..., pattern="^(image|video|url|pdf)$")


class AttachmentCreate(AttachmentBase):
    file_path: str


class Attachment(AttachmentBase):
    id: int
    journal_id: int
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True


# Journal tag schema
class JournalStudentTagBase(BaseModel):
    student_id: int


class JournalStudentTagCreate(JournalStudentTagBase):
    pass


class JournalStudentTag(JournalStudentTagBase):
    id: int
    journal_id: int
    created_at: datetime
    student: Optional[User] = None

    class Config:
        orm_mode = True


# Journal schema
class JournalBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str


class JournalCreate(JournalBase):
    student_ids: List[int] = []
    published_at: Optional[datetime] = None


class JournalUpdate(JournalBase):
    student_ids: Optional[List[int]] = None
    published_at: Optional[datetime] = None


class JournalPublish(BaseModel):
    published_at: Optional[datetime] = None


class Journal(JournalBase):
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    is_published: bool
    teacher: Optional[User] = None
    attachments: List[Attachment] = []
    tagged_students: List[JournalStudentTag] = []

    class Config:
        orm_mode = True


# Journal with fewer details for list views
class JournalBrief(BaseModel):
    id: int
    title: str
    teacher_id: int
    created_at: datetime
    published_at: Optional[datetime] = None
    is_published: bool

    class Config:
        orm_mode = True