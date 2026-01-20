"""Pydantic schemas for Authentication."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # seconds


class TokenData(BaseModel):
    """Data encoded in JWT token."""
    user_id: str
    email: str
    exp: Optional[datetime] = None


class GoogleAuthRequest(BaseModel):
    """Request for Google OAuth authentication."""
    credential: str = Field(..., description="Google ID token from frontend")


class GoogleUserInfo(BaseModel):
    """User info from Google."""
    google_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    email_verified: bool = True


class OrganizationInfo(BaseModel):
    """Organization info for auth response."""
    id: str
    name: str
    slug: str
    role: str
    logo_url: Optional[str] = None


class UserInfo(BaseModel):
    """User info for auth response."""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthResponse(BaseModel):
    """Response after successful authentication."""
    token: Token
    user: UserInfo
    organizations: List[OrganizationInfo] = []
    is_new_user: bool = False
    needs_organization: bool = False


class OnboardingRequest(BaseModel):
    """Request for new user onboarding - create first organization."""
    organization_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = None


class AcceptInviteRequest(BaseModel):
    """Request to accept an organization invite."""
    invite_token: str
