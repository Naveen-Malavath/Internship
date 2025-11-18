"""Pydantic models for Design resources."""

from datetime import datetime

from pydantic import BaseModel


class DesignBase(BaseModel):
    """Base schema for Design documents."""

    project_id: str
    hld_mermaid: str
    lld_mermaid: str
    dbd_mermaid: str
    created_at: datetime

    class Config:
        """Pydantic configuration."""

        orm_mode = True


class DesignResponse(DesignBase):
    """Schema returned to clients when fetching a design."""

    _id: str

