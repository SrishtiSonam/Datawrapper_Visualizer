from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.database import get_db
from app.routers.auth import get_current_user, get_current_teacher, get_current_student

router = APIRouter(tags=["journals"], prefix="/journals")


@router.get("/", response_model=List[schemas.Journal])
def get_journals(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get journal feed based on user type.
    - Teacher: all journals created by the teacher
    - Student: all journals where the student is tagged
    """
    if current_user.is_teacher():
        journals = services.journal.get_journals_for_teacher(db, current_user.id, skip, limit)
    else:
        journals = services.journal.get_journals_for_student(db, current_user.id, skip, limit)

    return journals


@router.get("/{journal_id}", response_model=schemas.Journal)
def get_journal(
    journal_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific journal by ID.
    """
    db_journal = services.journal.get_journal(db, journal_id)

    if not db_journal:
        raise HTTPException(status_code=404, detail="Journal not found")

    # Check if user is authorized to view the journal
    if current_user.is_teacher():
        if db_journal.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this journal")
    else:  # Student
        # Check if student is tagged in the journal
        is_tagged = False
        for tag in db_journal.tagged_students:
            if tag.student_id == current_user.id:
                is_tagged = True
                break

        if not is_tagged:
            raise HTTPException(status_code=403, detail="Not authorized to access this journal")

        # Check if journal is published and not scheduled for future
        if not db_journal.is_published or (db_journal.published_at and db_journal.published_at > datetime.utcnow()):
            raise HTTPException(status_code=403, detail="Journal is not yet published")

    return db_journal


@router.post("/", response_model=schemas.Journal)
def create_journal(
    journal: schemas.JournalCreate,
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Create a new journal (teachers only).
    """
    return services.journal.create_journal(db, journal, current_teacher.id)


@router.put("/{journal_id}", response_model=schemas.Journal)
def update_journal(
    journal_id: int,
    journal: schemas.JournalUpdate,
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Update an existing journal (teachers only).
    """
    db_journal = services.journal.update_journal(db, journal_id, journal, current_teacher.id)

    if not db_journal:
        raise HTTPException(status_code=404, detail="Journal not found or not authorized")

    return db_journal


@router.delete("/{journal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal(
    journal_id: int,
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Delete a journal (teachers only).
    """
    result = services.journal.delete_journal(db, journal_id, current_teacher.id)

    if not result:
        raise HTTPException(status_code=404, detail="Journal not found or not authorized")

    return None


@router.post("/{journal_id}/publish", response_model=schemas.Journal)
def publish_journal(
    journal_id: int,
    publish_data: schemas.JournalPublish,
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Publish a journal (teachers only).
    """
    db_journal = services.journal.publish_journal(db, journal_id, publish_data, current_teacher.id)

    if not db_journal:
        raise HTTPException(status_code=404, detail="Journal not found or not authorized")

    return db_journal


@router.post("/{journal_id}/attachments", response_model=schemas.Attachment)
async def add_attachment(
    journal_id: int,
    file: UploadFile = File(...),
    attachment_type: str = Form(...),
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Add an attachment to a journal (teachers only).
    """
    db_attachment = services.journal.add_attachment(
        db, journal_id, current_teacher.id, file, attachment_type
    )

    if not db_attachment:
        raise HTTPException(status_code=404, detail="Journal not found or not authorized")

    return db_attachment


@router.delete("/{journal_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    journal_id: int,
    attachment_id: int,
    current_teacher: models.User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """
    Delete an attachment from a journal (teachers only).
    """
    result = services.journal.delete_attachment(db, attachment_id, current_teacher.id)

    if not result:
        raise HTTPException(status_code=404, detail="Attachment not found or not authorized")

    return None