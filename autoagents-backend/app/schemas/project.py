"""Pydantic models for Project resources."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""

    user_id: str
    title: str = Field(min_length=3, max_length=180)
    prompt: str = Field(min_length=10)
    status: str = Field(default="created")


class ProjectResponse(BaseModel):
    """Schema returned to clients when fetching a project."""

    id: str
    user_id: str
    title: str
    prompt: str
    status: str
    created_at: datetime

