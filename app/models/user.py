from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum("teacher", "student"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    journals = relationship("Journal", back_populates="teacher", cascade="all, delete-orphan")
    tagged_journals = relationship("JournalStudentTag", back_populates="student")
    notifications = relationship("Notification", back_populates="student", cascade="all, delete-orphan")

    def is_teacher(self):
        return self.user_type == "teacher"

    def is_student(self):
        return self.user_type == "student"