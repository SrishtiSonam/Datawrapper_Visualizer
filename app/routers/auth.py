from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app import models, schemas, services
from app.database import get_db
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["authentication"])

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and provide access token.

    Note: For this mock authentication, any username/password combination is accepted.
    If the username doesn't exist, a new user will be created.
    """
    # Try to find the user
    user = services.auth.authenticate_user(db, form_data.username, form_data.password)

    # If user doesn't exist, create a new one (for demo purposes)
    if not user:
        # Default to student type
        user_type = "student"
        if form_data.username.startswith("teacher"):
            user_type = "teacher"

        # Create a new user
        hashed_password = services.auth.get_password_hash(form_data.password)
        user = models.User(
            username=form_data.username,
            password_hash=hashed_password,
            user_type=user_type
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = services.auth.create_access_token(
        data={"sub": user.id, "user_type": user.user_type},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Get the current authenticated user based on the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: Optional[int] = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_teacher(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Get the current user and verify that they are a teacher.
    """
    if not current_user.is_teacher():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Teacher role required."
        )
    return current_user


def get_current_student(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    Get the current user and verify that they are a student.
    """
    if not current_user.is_student():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Student role required."
        )
    return current_user