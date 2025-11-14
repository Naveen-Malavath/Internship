"""Pydantic models for User resources."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user (password hashing applied later)."""

    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """Schema returned to clients after user creation/login."""

    id: str
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime

