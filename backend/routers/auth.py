"""
Authentication router with Google OAuth support.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database.config import get_db
from database.models import User, Organization, OrganizationMember, OrgRole, MemberStatus
from schemas.auth import (
    Token, TokenData, GoogleAuthRequest, AuthResponse, 
    OnboardingRequest, AcceptInviteRequest,
    UserInfo, OrganizationInfo
)
from schemas.user import UserCreate
from crud.user import (
    get_user, get_user_by_email, get_user_by_google_id,
    create_user, update_user_last_login
)
from crud.organization import (
    get_user_organizations, create_organization,
    get_organization_invite_by_token, accept_organization_invite,
    get_pending_invites_for_email
)
from schemas.organization import OrganizationCreate

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Security
security = HTTPBearer(auto_error=False)

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-use-env-var")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Google OAuth Settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=user_id, email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(credentials.credentials)
    user = get_user(db, token_data.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    
    try:
        token_data = verify_token(credentials.credentials)
        return get_user(db, token_data.user_id)
    except HTTPException:
        return None


def verify_google_token(token: str) -> dict:
    """Verify Google ID token and return user info."""
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Check issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
        
        return {
            "google_id": idinfo['sub'],
            "email": idinfo['email'],
            "name": idinfo.get('name'),
            "picture": idinfo.get('picture'),
            "email_verified": idinfo.get('email_verified', True),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )


def get_user_orgs_info(db: Session, user_id: str) -> list[OrganizationInfo]:
    """Get organization info for a user."""
    memberships = (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == MemberStatus.ACTIVE
        )
        .all()
    )
    
    orgs = []
    for membership in memberships:
        org = membership.organization
        orgs.append(OrganizationInfo(
            id=org.id,
            name=org.name,
            slug=org.slug,
            role=membership.role.value,
            logo_url=org.logo_url,
        ))
    
    return orgs


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate with Google OAuth.
    
    - If user exists: login and return token
    - If user is new: create account and return token with needs_organization flag
    """
    # Verify Google token
    google_info = verify_google_token(request.credential)
    
    # Check if user exists
    user = get_user_by_google_id(db, google_info["google_id"])
    is_new_user = False
    
    if not user:
        # Check by email (user might exist but not linked to Google)
        user = get_user_by_email(db, google_info["email"])
        
        if user:
            # Link Google account to existing user
            user.google_id = google_info["google_id"]
            if not user.avatar_url and google_info.get("picture"):
                user.avatar_url = google_info["picture"]
            db.commit()
        else:
            # Create new user
            user_data = UserCreate(
                email=google_info["email"],
                google_id=google_info["google_id"],
                name=google_info.get("name"),
                avatar_url=google_info.get("picture"),
            )
            user = create_user(db, user_data)
            is_new_user = True
    
    # Update last login
    update_user_last_login(db, user.id)
    
    # Check for pending invites
    pending_invites = get_pending_invites_for_email(db, user.email)
    
    # Get user's organizations
    orgs = get_user_orgs_info(db, user.id)
    needs_organization = len(orgs) == 0 and len(pending_invites) == 0
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return AuthResponse(
        token=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        user=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
        ),
        organizations=orgs,
        is_new_user=is_new_user,
        needs_organization=needs_organization,
    )


@router.post("/onboarding", response_model=AuthResponse)
async def complete_onboarding(
    request: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete onboarding by creating the user's first organization.
    """
    # Create organization
    org_data = OrganizationCreate(
        name=request.organization_name,
        settings={"default_industry": request.industry} if request.industry else {},
    )
    org = create_organization(db, org_data, current_user.id)
    
    # Get updated orgs
    orgs = get_user_orgs_info(db, current_user.id)
    
    # Create new token (refresh)
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email}
    )
    
    return AuthResponse(
        token=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        user=UserInfo(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
        ),
        organizations=orgs,
        is_new_user=False,
        needs_organization=False,
    )


@router.post("/accept-invite", response_model=AuthResponse)
async def accept_invite(
    request: AcceptInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accept an organization invite.
    """
    # Get invite
    invite = get_organization_invite_by_token(db, request.invite_token)
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found or expired",
        )
    
    if invite.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite already accepted",
        )
    
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite has expired",
        )
    
    if invite.email.lower() != current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invite is for a different email address",
        )
    
    # Accept invite
    accept_organization_invite(db, invite, current_user.id)
    
    # Get updated orgs
    orgs = get_user_orgs_info(db, current_user.id)
    
    # Create new token
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email}
    )
    
    return AuthResponse(
        token=Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
        user=UserInfo(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
        ),
        organizations=orgs,
        is_new_user=False,
        needs_organization=False,
    )


@router.get("/me", response_model=AuthResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user info and their organizations.
    """
    orgs = get_user_orgs_info(db, current_user.id)
    
    return AuthResponse(
        token=Token(access_token="", token_type="bearer", expires_in=0),  # Token not refreshed here
        user=UserInfo(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
        ),
        organizations=orgs,
        is_new_user=False,
        needs_organization=len(orgs) == 0,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh the access token.
    """
    access_token = create_access_token(
        data={"sub": current_user.id, "email": current_user.email}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
