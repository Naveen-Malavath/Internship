"""Pydantic schemas for Wireframe entities."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DesignStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"


class WireframeComponentType(str, Enum):
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    PAGE_WRAPPER = "page_wrapper"


# ============================================================================
# Wireframe Page
# ============================================================================

class WireframePageBase(BaseModel):
    """Base wireframe page schema."""
    page_name: str = Field(..., min_length=1, max_length=255)
    page_type: Optional[str] = None
    html_content: Optional[str] = None
    description: Optional[str] = None


class WireframePageCreate(WireframePageBase):
    """Schema for creating a wireframe page."""
    order_index: int = 0
    status: DesignStatus = DesignStatus.PENDING


class WireframePageUpdate(BaseModel):
    """Schema for updating a wireframe page."""
    page_name: Optional[str] = Field(None, min_length=1, max_length=255)
    page_type: Optional[str] = None
    html_content: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    status: Optional[DesignStatus] = None
    error_message: Optional[str] = None


class WireframePageResponse(WireframePageBase):
    """Schema for wireframe page API responses."""
    id: str
    project_id: str
    order_index: int = 0
    status: DesignStatus = DesignStatus.PENDING
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Wireframe Component
# ============================================================================

class WireframeComponentBase(BaseModel):
    """Base wireframe component schema."""
    component_type: WireframeComponentType
    html_content: Optional[str] = None


class WireframeComponentCreate(WireframeComponentBase):
    """Schema for creating a wireframe component."""
    pass


class WireframeComponentResponse(WireframeComponentBase):
    """Schema for wireframe component API responses."""
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Combined Response
# ============================================================================

class WireframeDataResponse(BaseModel):
    """Combined wireframe data response."""
    pages: List[WireframePageResponse]
    components: List[WireframeComponentResponse]
    total_pages: int
