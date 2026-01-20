"""Pydantic schemas for Project entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    GENERATING = "generating"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=255)
    key: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = None
    team_size: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""
    executive_summary: Optional[str] = None
    prompt_summary: Optional[str] = None
    final_prompt: Optional[str] = None
    risk_highlights: List[str] = Field(default_factory=list)
    generated_risks: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    extra_data: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    key: Optional[str] = None
    industry: Optional[str] = None
    team_size: Optional[str] = None
    executive_summary: Optional[str] = None
    prompt_summary: Optional[str] = None
    final_prompt: Optional[str] = None
    risk_highlights: Optional[List[str]] = None
    generated_risks: Optional[str] = None
    status: Optional[ProjectStatus] = None
    settings: Optional[Dict[str, Any]] = None
    extra_data: Optional[Dict[str, Any]] = None


class ProjectResponse(ProjectBase):
    """Schema for project API responses."""
    id: str
    organization_id: str
    created_by: str
    executive_summary: Optional[str] = None
    prompt_summary: Optional[str] = None
    final_prompt: Optional[str] = None
    risk_highlights: List[str] = Field(default_factory=list)
    generated_risks: Optional[str] = None
    status: ProjectStatus = ProjectStatus.DRAFT
    settings: Dict[str, Any] = Field(default_factory=dict)
    extra_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Counts
    feature_count: Optional[int] = None
    story_count: Optional[int] = None
    design_count: Optional[int] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Schema for project list with pagination."""
    projects: List[ProjectResponse]
    total: int
    page: int = 1
    page_size: int = 20
