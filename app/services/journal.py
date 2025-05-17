from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import os
import uuid
import shutil

from app import models, schemas
from app.config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS


def get_journals_for_teacher(db: Session, teacher_id: int, skip: int = 0, limit: int = 100):
    """Get journals created by a specific teacher."""
    return (
        db.query(models.Journal)
        .filter(models.Journal.teacher_id == teacher_id)
        .order_by(models.Journal.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_journals_for_student(db: Session, student_id: int, skip: int = 0, limit: int = 100):
    """Get journals where a specific student is tagged."""
    now = datetime.utcnow()

    return (
        db.query(models.Journal)
        .join(models.JournalStudentTag, models.Journal.id == models.JournalStudentTag.journal_id)
        .filter(
            models.JournalStudentTag.student_id == student_id,
            models.Journal.is_published == True,
            (models.Journal.published_at <= now) | (models.Journal.published_at == None)
        )
        .order_by(models.Journal.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_journal(db: Session, journal_id: int):
    """Get a specific journal by ID."""
    return db.query(models.Journal).filter(models.Journal.id == journal_id).first()


def create_journal(db: Session, journal: schemas.JournalCreate, teacher_id: int):
    """Create a new journal."""
    db_journal = models.Journal(
        title=journal.title,
        description=journal.description,
        teacher_id=teacher_id,
        published_at=journal.published_at,
        is_published=journal.published_at is not None and journal.published_at <= datetime.utcnow(),
    )

    db.add(db_journal)
    db.flush()

    # Add student tags
    for student_id in journal.student_ids:
        db_tag = models.JournalStudentTag(
            journal_id=db_journal.id,
            student_id=student_id,
        )
        db.add(db_tag)

    db.commit()
    db.refresh(db_journal)

    # Create notifications for tagged students (if the journal is published)
    if db_journal.is_published:
        create_notifications_for_journal(db, db_journal)

    return db_journal


def update_journal(db: Session, journal_id: int, journal: schemas.JournalUpdate, teacher_id: int):
    """Update an existing journal."""
    db_journal = get_journal(db, journal_id)

    if not db_journal:
        return None

    if db_journal.teacher_id != teacher_id:
        return None

    # Update journal fields
    db_journal.title = journal.title
    db_journal.description = journal.description

    # Update published_at if provided
    if journal.published_at is not None:
        was_published = db_journal.is_published
        db_journal.published_at = journal.published_at
        db_journal.is_published = journal.published_at <= datetime.utcnow()

        # If journal was not published before but now is, create notifications
        if not was_published and db_journal.is_published:
            create_notifications_for_journal(db, db_journal)

    # Update student tags if provided
    if journal.student_ids is not None:
        # Delete existing tags
        db.query(models.JournalStudentTag).filter(
            models.JournalStudentTag.journal_id == journal_id
        ).delete()

        # Add new tags
        for student_id in journal.student_ids:
            db_tag = models.JournalStudentTag(
                journal_id=journal_id,
                student_id=student_id,
            )
            db.add(db_tag)

    db.commit()
    db.refresh(db_journal)

    return db_journal


def delete_journal(db: Session, journal_id: int, teacher_id: int):
    """Delete a journal."""
    db_journal = get_journal(db, journal_id)

    if not db_journal:
        return False

    if db_journal.teacher_id != teacher_id:
        return False

    # Delete attachments from filesystem
    for attachment in db_journal.attachments:
        try:
            file_path = os.path.join(os.getcwd(), attachment.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Log error but continue with deletion
            print(f"Error deleting file: {e}")

    # Delete journal from database
    db.delete(db_journal)
    db.commit()

    return True


def publish_journal(db: Session, journal_id: int, publish_data: schemas.JournalPublish, teacher_id: int):
    """Publish a journal."""
    db_journal = get_journal(db, journal_id)

    if not db_journal:
        return None

    if db_journal.teacher_id != teacher_id:
        return None

    # Set published_at time (use current time if none provided)
    published_at = publish_data.published_at if publish_data.published_at else datetime.utcnow()
    db_journal.published_at = published_at
    db_journal.is_published = True

    db.commit()
    db.refresh(db_journal)

    # Create notifications for tagged students
    create_notifications_for_journal(db, db_journal)

    return db_journal


def add_attachment(db: Session, journal_id: int, teacher_id: int, file: UploadFile, attachment_type: str):
    """Add an attachment to a journal."""
    db_journal = get_journal(db, journal_id)

    if not db_journal:
        return None

    if db_journal.teacher_id != teacher_id:
        return None

    # Check if attachment type is valid
    if attachment_type not in ["image", "video", "url", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid attachment type")

    # Validate file extension
    if attachment_type != "url":
        file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
        if file_ext not in ALLOWED_EXTENSIONS.get(attachment_type, []):
            raise HTTPException(
                status_code=400,
                detail=f"File extension '.{file_ext}' not allowed for {attachment_type}"
            )

    # Create uploads directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # For URL type, the file content is the URL itself
    if attachment_type == "url":
        url = file.filename
        db_attachment = models.Attachment(
            journal_id=journal_id,
            file_path=url,
            attachment_type=attachment_type
        )
    else:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create attachment record
        db_attachment = models.Attachment(
            journal_id=journal_id,
            file_path=file_path,
            attachment_type=attachment_type
        )

    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)

    return db_attachment


def delete_attachment(db: Session, attachment_id: int, teacher_id: int):
    """Delete an attachment."""
    db_attachment = db.query(models.Attachment).filter(models.Attachment.id == attachment_id).first()

    if not db_attachment:
        return False

    # Check if the teacher owns the journal
    db_journal = get_journal(db, db_attachment.journal_id)
    if not db_journal or db_journal.teacher_id != teacher_id:
        return False

    # Delete file if it's not a URL
    if db_attachment.attachment_type != "url":
        try:
            file_path = os.path.join(os.getcwd(), db_attachment.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Log error but continue with deletion
            print(f"Error deleting file: {e}")

    # Delete attachment record
    db.delete(db_attachment)
    db.commit()

    return True


def create_notifications_for_journal(db: Session, journal):
    """Create notifications for all students tagged in a journal."""
    for tag in journal.tagged_students:
        notification = models.Notification(
            student_id=tag.student_id,
            journal_id=journal.id,
            message=f"You've been tagged in a new journal: {journal.title}"
        )
        db.add(notification)

    db.commit()