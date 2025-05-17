from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas, services
from app.database import get_db
from app.routers.auth import get_current_user, get_current_student

router = APIRouter(tags=["notifications"], prefix="/notifications")


@router.get("/", response_model=List[schemas.Notification])
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    current_student: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get all notifications for the current student.
    """
    return services.notification.get_notifications_for_student(db, current_student.id, skip, limit)


@router.get("/unread", response_model=List[schemas.Notification])
def get_unread_notifications(
    current_student: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get unread notifications for the current student.
    """
    return services.notification.get_unread_notifications_for_student(db, current_student.id)


@router.put("/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_as_read(
    notification_id: int,
    current_student: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Mark a specific notification as read.
    """
    db_notification = services.notification.mark_notification_as_read(
        db, notification_id, current_student.id
    )

    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found or not authorized")

    return db_notification


@router.put("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_notifications_as_read(
    current_student: models.User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for the current student.
    """
    services.notification.mark_all_notifications_as_read(db, current_student.id)
    return None