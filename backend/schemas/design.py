"""Pydantic schemas for Design entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class DesignType(str, Enum):
    HLD = "hld"
    DBD = "dbd"
    API = "api"
    LLD = "lld"
    DFD = "dfd"
    COMPONENT = "component"
    SECURITY = "security"
    INFRASTRUCTURE = "infrastructure"
    STATE = "state"
    JOURNEY = "journey"
    SEQUENCE = "sequence"
    MINDMAP = "mindmap"
    GANTT = "gantt"
    GITFLOW = "gitflow"


class DesignStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class DesignBase(BaseModel):
    """Base design schema."""
    design_type: DesignType
    diagram: Optional[str] = None
    summary: Optional[str] = None


class DesignCreate(DesignBase):
    """Schema for creating a design."""
    status: DesignStatus = DesignStatus.PENDING
    tokens_used: Dict[str, int] = Field(default_factory=dict)


class DesignUpdate(BaseModel):
    """Schema for updating a design."""
    diagram: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[DesignStatus] = None
    tokens_used: Optional[Dict[str, int]] = None
    error_message: Optional[str] = None
    version: Optional[int] = None


class DesignResponse(DesignBase):
    """Schema for design API responses."""
    id: str
    project_id: str
    version: int = 1
    status: DesignStatus = DesignStatus.PENDING
    tokens_used: Dict[str, int] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DesignListResponse(BaseModel):
    """Schema for design list."""
    designs: List[DesignResponse]
    count: int
