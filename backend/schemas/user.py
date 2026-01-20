"""Pydantic schemas for User entities."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    google_id: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user API responses."""
    id: str
    google_id: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """User schema with all database fields."""
    pass
