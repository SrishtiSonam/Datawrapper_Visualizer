from sqlalchemy.orm import Session

from app import models, schemas


def get_notifications_for_student(db: Session, student_id: int, skip: int = 0, limit: int = 100):
    """Get all notifications for a specific student."""
    return (
        db.query(models.Notification)
        .filter(models.Notification.student_id == student_id)
        .order_by(models.Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_unread_notifications_for_student(db: Session, student_id: int):
    """Get unread notifications for a specific student."""
    return (
        db.query(models.Notification)
        .filter(
            models.Notification.student_id == student_id,
            models.Notification.is_read == False
        )
        .order_by(models.Notification.created_at.desc())
        .all()
    )


def mark_notification_as_read(db: Session, notification_id: int, student_id: int):
    """Mark a notification as read."""
    db_notification = (
        db.query(models.Notification)
        .filter(
            models.Notification.id == notification_id,
            models.Notification.student_id == student_id
        )
        .first()
    )

    if not db_notification:
        return None

    db_notification.is_read = True
    db.commit()
    db.refresh(db_notification)

    return db_notification


def mark_all_notifications_as_read(db: Session, student_id: int):
    """Mark all notifications as read for a student."""
    db.query(models.Notification).filter(
        models.Notification.student_id == student_id,
        models.Notification.is_read == False
    ).update({"is_read": True})

    db.commit()

    return True