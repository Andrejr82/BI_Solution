"""
User Schemas
Pydantic schemas for User API
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="viewer", pattern="^(admin|user|viewer)$")
    allowed_segments: list[str] = Field(default_factory=list) # Novo Campo


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = None
    role: str | None = Field(None, pattern="^(admin|user|viewer)$")
    is_active: bool | None = None
    allowed_segments: list[str] | None = Field(None) # Novo Campo
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(UserBase):
    """Schema for user response"""

    id: uuid.UUID
    role: str
    is_active: bool
    allowed_segments: list[str] # Novo Campo
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)"""

    hashed_password: str
