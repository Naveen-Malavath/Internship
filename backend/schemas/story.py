"""Pydantic schemas for Story entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class StoryBase(BaseModel):
    """Base story schema."""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    feature_ref: Optional[str] = None
    feature_context: Optional[str] = None


class StoryCreate(StoryBase):
    """Schema for creating a story."""
    feature_id: str
    order_index: int = 0
    approved: bool = False
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class StoryUpdate(BaseModel):
    """Schema for updating a story."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    feature_ref: Optional[str] = None
    feature_context: Optional[str] = None
    order_index: Optional[int] = None
    approved: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None


class StoryResponse(StoryBase):
    """Schema for story API responses."""
    id: str
    project_id: str
    feature_id: str
    order_index: int = 0
    approved: bool = False
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Include feature title for display
    feature_title: Optional[str] = None

    class Config:
        from_attributes = True


class StoryBulkCreate(BaseModel):
    """Schema for creating multiple stories at once."""
    stories: List[StoryCreate]


class StoryBulkResponse(BaseModel):
    """Response for bulk story creation."""
    created: List[StoryResponse]
    count: int
