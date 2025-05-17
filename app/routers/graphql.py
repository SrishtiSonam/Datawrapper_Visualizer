from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.journal import Journal, Attachment, JournalStudentTag
from app.models.notification import Notification
from app.services.auth import get_current_user

# GraphQL Types
@strawberry.type
class UserType:
    id: int
    username: str
    user_type: str
    created_at: datetime

@strawberry.type
class JournalType:
    id: int
    title: str
    description: str
    teacher_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    is_published: bool
    attachments: List["AttachmentType"]
    tagged_students: List["UserType"]

@strawberry.type
class AttachmentType:
    id: int
    journal_id: int
    file_path: str
    attachment_type: str
    created_at: datetime

@strawberry.type
class NotificationType:
    id: int
    student_id: int
    journal_id: int
    message: str
    is_read: bool
    created_at: datetime

# Context class to pass dependencies
class Context:
    def __init__(self, db: Session, current_user: Optional[User] = None):
        self.db = db
        self.current_user = current_user

# GraphQL Queries
@strawberry.type
class Query:
    @strawberry.field
    def user(self, info, id: int) -> Optional[UserType]:
        db = info.context.db
        current_user = info.context.current_user

        if not current_user:
            return None

        user = db.query(User).filter(User.id == id).first()
        return user if user else None

    @strawberry.field
    def journal(self, info, id: int) -> Optional[JournalType]:
        db = info.context.db
        current_user = info.context.current_user

        if not current_user:
            return None

        journal = db.query(Journal).filter(Journal.id == id).first()

        # Check access permissions
        if not journal.is_published and journal.teacher_id != current_user.id:
            tagged = db.query(JournalStudentTag).filter(
                JournalStudentTag.journal_id == id,
                JournalStudentTag.student_id == current_user.id
            ).first()
            if not tagged:
                return None

        return journal

    @strawberry.field
    def journals(self, info) -> List[JournalType]:
        db = info.context.db
        current_user = info.context.current_user

        if not current_user:
            return []

        if current_user.user_type == "teacher":
            # Teachers see their own journals
            journals = db.query(Journal).filter(Journal.teacher_id == current_user.id).all()
        else:
            # Students see published journals or journals they're tagged in
            tagged_journals = db.query(Journal).join(
                JournalStudentTag,
                JournalStudentTag.journal_id == Journal.id
            ).filter(JournalStudentTag.student_id == current_user.id).all()

            published_journals = db.query(Journal).filter(Journal.is_published == True).all()

            # Combine and remove duplicates
            journal_ids = set()
            journals = []

            for journal in tagged_journals + published_journals:
                if journal.id not in journal_ids:
                    journal_ids.add(journal.id)
                    journals.append(journal)

        return journals

    @strawberry.field
    def notifications(self, info) -> List[NotificationType]:
        db = info.context.db
        current_user = info.context.current_user

        if not current_user:
            return []

        notifications = db.query(Notification).filter(
            Notification.student_id == current_user.id
        ).order_by(Notification.created_at.desc()).all()

        return notifications

# GraphQL Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    def mark_notification_as_read(self, info, notification_id: int) -> bool:
        db = info.context.db
        current_user = info.context.current_user

        if not current_user:
            return False

        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.student_id == current_user.id
        ).first()

        if not notification:
            return False

        notification.is_read = True
        db.commit()
        return True

# Create schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

async def get_context(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return Context(db=db, current_user=current_user)

# Create GraphQL router
graphql_router = GraphQLRouter(
    schema=schema,
    context_getter=get_context,
    graphiql=True  # Enable GraphiQL interface for testing
)

# Create FastAPI router
router = APIRouter()

# Include GraphQL router
router.include_router(graphql_router, prefix="")