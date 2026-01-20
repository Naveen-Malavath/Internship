"""Pydantic schemas for Organization entities."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class OrgRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class OrgPlan(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class MemberStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


# ============================================================================
# Organization
# ============================================================================

class OrganizationBase(BaseModel):
    """Base organization schema."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""
    settings: Dict[str, Any] = Field(default_factory=dict)


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class OrganizationResponse(OrganizationBase):
    """Schema for organization API responses."""
    id: str
    settings: Dict[str, Any] = Field(default_factory=dict)
    plan: OrgPlan = OrgPlan.FREE
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Organization Member
# ============================================================================

class OrganizationMemberBase(BaseModel):
    """Base organization member schema."""
    role: OrgRole = OrgRole.MEMBER


class OrganizationMemberCreate(OrganizationMemberBase):
    """Schema for adding a member to organization."""
    user_id: str


class OrganizationMemberResponse(BaseModel):
    """Schema for organization member API responses."""
    id: str
    organization_id: str
    user_id: str
    role: OrgRole
    status: MemberStatus
    invited_by: Optional[str] = None
    joined_at: Optional[datetime] = None
    created_at: datetime

    # Include user details
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    user_avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationWithMembers(OrganizationResponse):
    """Organization with its members."""
    members: List[OrganizationMemberResponse] = []
    member_count: int = 0
    project_count: int = 0


# ============================================================================
# Organization Invite
# ============================================================================

class OrganizationInviteCreate(BaseModel):
    """Schema for creating an invitation."""
    email: str = Field(..., description="Email to invite")
    role: OrgRole = OrgRole.MEMBER


class OrganizationInviteResponse(BaseModel):
    """Schema for invitation API responses."""
    id: str
    organization_id: str
    email: str
    role: OrgRole
    token: str
    invited_by: str
    expires_at: datetime
    accepted_at: Optional[datetime] = None
    created_at: datetime

    # Include organization name for display
    organization_name: Optional[str] = None

    class Config:
        from_attributes = True
