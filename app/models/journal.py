from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    is_published = Column(Boolean, default=False)

    # Relationships
    teacher = relationship("User", back_populates="journals")
    attachments = relationship("Attachment", back_populates="journal", cascade="all, delete-orphan")
    tagged_students = relationship("JournalStudentTag", back_populates="journal", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="journal", cascade="all, delete-orphan")

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    file_path = Column(String(255), nullable=False)
    attachment_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    journal = relationship("Journal", back_populates="attachments")

class JournalStudentTag(Base):
    __tablename__ = "journal_student_tags"

    id = Column(Integer, primary_key=True, index=True)
    journal_id = Column(Integer, ForeignKey("journals.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    journal = relationship("Journal", back_populates="tagged_students")
    student = relationship("User", back_populates="tagged_journals")