"""Pydantic schemas for Generated App entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class AppStatus(str, Enum):
    CREATED = "created"
    BUILDING = "building"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class GeneratedAppBase(BaseModel):
    """Base generated app schema."""
    safe_name: str = Field(..., min_length=1, max_length=255)
    project_path: Optional[str] = None


class GeneratedAppCreate(GeneratedAppBase):
    """Schema for creating a generated app record."""
    frontend_port: Optional[int] = None
    backend_port: Optional[int] = None
    preview_url: Optional[str] = None
    docker_compose: Optional[str] = None
    frontend_files: Dict[str, str] = Field(default_factory=dict)
    backend_files: Dict[str, str] = Field(default_factory=dict)
    status: AppStatus = AppStatus.CREATED


class GeneratedAppUpdate(BaseModel):
    """Schema for updating a generated app."""
    project_path: Optional[str] = None
    frontend_port: Optional[int] = None
    backend_port: Optional[int] = None
    preview_url: Optional[str] = None
    status: Optional[AppStatus] = None
    docker_compose: Optional[str] = None
    frontend_files: Optional[Dict[str, str]] = None
    backend_files: Optional[Dict[str, str]] = None
    build_log: Optional[str] = None
    error_log: Optional[str] = None


class GeneratedAppResponse(GeneratedAppBase):
    """Schema for generated app API responses."""
    id: str
    project_id: str
    frontend_port: Optional[int] = None
    backend_port: Optional[int] = None
    preview_url: Optional[str] = None
    status: AppStatus = AppStatus.CREATED
    docker_compose: Optional[str] = None
    frontend_files: Dict[str, str] = Field(default_factory=dict)
    backend_files: Dict[str, str] = Field(default_factory=dict)
    build_log: Optional[str] = None
    error_log: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GeneratedAppListResponse(BaseModel):
    """Schema for generated app list."""
    apps: List[GeneratedAppResponse]
    count: int
