"""Pydantic models for Feedback documents."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request model for feedback submission and regeneration."""

    itemId: str = Field(..., description="ID of the item (feature/story/visualization)")
    itemType: str = Field(..., description="Type of item: 'feature', 'story', or 'visualization'")
    projectId: str = Field(..., description="Project ID")
    feedback: str = Field(..., description="User feedback text")
    originalContent: Optional[Dict[str, Any]] = Field(None, description="Original content to regenerate")
    projectContext: Optional[str] = Field(None, description="Original project prompt/context")
    regenerate: Optional[bool] = Field(False, description="Whether to immediately regenerate")


class FeedbackResponse(BaseModel):
    """Response model for feedback operations."""

    feedbackId: str = Field(..., description="ID of the feedback entry")
    regenerationCount: int = Field(..., description="Current regeneration count for this item")
    autoRegenerate: Optional[bool] = Field(None, description="Whether auto-regeneration was triggered")
    regeneratedContent: Optional[Dict[str, Any]] = Field(None, description="Regenerated content")
    version: Optional[int] = Field(None, description="Version number of regenerated content")
    message: Optional[str] = Field(None, description="Response message")


class FeedbackHistoryEntry(BaseModel):
    """Model for feedback history entries."""

    id: str
    itemId: str
    itemType: str
    feedback: str
    timestamp: str
    status: str  # 'submitted', 'regenerated', 'failed'
    regeneratedAt: Optional[str] = None
    version: Optional[int] = None


class RegenerationCountResponse(BaseModel):
    """Response model for regeneration count query."""

    count: int = Field(..., description="Current regeneration count")

