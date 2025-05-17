from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)

# Properties for creating user
class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    user_type: str = Field(..., pattern="^(teacher|student)$")

# Properties for user authentication
class UserLogin(BaseModel):
    username: str
    password: str

# Properties to receive via API
class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=6)

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    user_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Additional properties to return via API
class User(UserInDBBase):
    pass

# Properties stored in DB but not returned by API
class UserInDB(UserInDBBase):
    password_hash: str

# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str

# Token payload
class TokenPayload(BaseModel):
    sub: Optional[int] = None
    user_type: Optional[str] = None