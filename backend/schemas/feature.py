"""Pydantic schemas for Feature entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class FeatureBase(BaseModel):
    """Base feature schema."""
    title: str = Field(..., min_length=1, max_length=500)
    reason: Optional[str] = None
    problem_statement: Optional[str] = None
    business_objective: Optional[str] = None
    user_persona: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    detailed_description: Optional[str] = None
    success_metrics: Optional[str] = None
    dependencies: Optional[str] = None


class FeatureCreate(FeatureBase):
    """Schema for creating a feature."""
    order_index: int = 0
    approved: bool = False
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class FeatureUpdate(BaseModel):
    """Schema for updating a feature."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    reason: Optional[str] = None
    problem_statement: Optional[str] = None
    business_objective: Optional[str] = None
    user_persona: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    detailed_description: Optional[str] = None
    success_metrics: Optional[str] = None
    dependencies: Optional[str] = None
    order_index: Optional[int] = None
    approved: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None


class FeatureResponse(FeatureBase):
    """Schema for feature API responses."""
    id: str
    project_id: str
    order_index: int = 0
    approved: bool = False
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Include story count
    story_count: Optional[int] = None

    class Config:
        from_attributes = True


class FeatureBulkCreate(BaseModel):
    """Schema for creating multiple features at once."""
    features: List[FeatureCreate]


class FeatureBulkResponse(BaseModel):
    """Response for bulk feature creation."""
    created: List[FeatureResponse]
    count: int
