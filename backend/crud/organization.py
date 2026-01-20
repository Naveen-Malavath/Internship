"""CRUD operations for Organization entities."""
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from database.models import (
    Organization, OrganizationMember, OrganizationInvite, User,
    OrgRole, MemberStatus
)
from schemas.organization import (
    OrganizationCreate, OrganizationUpdate,
    OrganizationMemberCreate, OrganizationInviteCreate
)


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:100]


def get_organization(db: Session, org_id: str) -> Optional[Organization]:
    """Get organization by ID."""
    return db.query(Organization).filter(Organization.id == org_id).first()


def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
    """Get organization by slug."""
    return db.query(Organization).filter(Organization.slug == slug).first()


def get_user_organizations(db: Session, user_id: str) -> List[Organization]:
    """Get all organizations a user belongs to."""
    return (
        db.query(Organization)
        .join(OrganizationMember)
        .filter(
            OrganizationMember.user_id == user_id,
            OrganizationMember.status == MemberStatus.ACTIVE
        )
        .all()
    )


def create_organization(
    db: Session, 
    org_data: OrganizationCreate, 
    creator_id: str
) -> Organization:
    """Create a new organization and add creator as owner."""
    # Generate unique slug
    base_slug = slugify(org_data.name)
    slug = base_slug
    counter = 1
    while get_organization_by_slug(db, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    db_org = Organization(
        name=org_data.name,
        slug=slug,
        description=org_data.description,
        logo_url=org_data.logo_url,
        settings=org_data.settings,
        created_by=creator_id,
    )
    db.add(db_org)
    db.flush()  # Get the ID
    
    # Add creator as owner
    db_member = OrganizationMember(
        organization_id=db_org.id,
        user_id=creator_id,
        role=OrgRole.OWNER,
        status=MemberStatus.ACTIVE,
        joined_at=datetime.utcnow(),
    )
    db.add(db_member)
    
    db.commit()
    db.refresh(db_org)
    return db_org


def update_organization(
    db: Session, 
    org_id: str, 
    org_data: OrganizationUpdate
) -> Optional[Organization]:
    """Update an organization."""
    db_org = get_organization(db, org_id)
    if not db_org:
        return None
    
    update_data = org_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_org, field, value)
    
    db_org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_org)
    return db_org


def delete_organization(db: Session, org_id: str) -> bool:
    """Delete an organization (cascades to all related data)."""
    db_org = get_organization(db, org_id)
    if not db_org:
        return False
    
    db.delete(db_org)
    db.commit()
    return True


# ============================================================================
# Organization Members
# ============================================================================

def get_organization_member(
    db: Session, 
    org_id: str, 
    user_id: str
) -> Optional[OrganizationMember]:
    """Get a specific member of an organization."""
    return (
        db.query(OrganizationMember)
        .filter(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id
        )
        .first()
    )


def get_organization_members(db: Session, org_id: str) -> List[OrganizationMember]:
    """Get all members of an organization."""
    return (
        db.query(OrganizationMember)
        .filter(OrganizationMember.organization_id == org_id)
        .all()
    )


def add_organization_member(
    db: Session,
    org_id: str,
    user_id: str,
    role: OrgRole = OrgRole.MEMBER,
    invited_by: Optional[str] = None
) -> OrganizationMember:
    """Add a member to an organization."""
    db_member = OrganizationMember(
        organization_id=org_id,
        user_id=user_id,
        role=role,
        status=MemberStatus.ACTIVE,
        invited_by=invited_by,
        invited_at=datetime.utcnow() if invited_by else None,
        joined_at=datetime.utcnow(),
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def update_organization_member(
    db: Session,
    org_id: str,
    user_id: str,
    role: Optional[OrgRole] = None,
    status: Optional[MemberStatus] = None
) -> Optional[OrganizationMember]:
    """Update a member's role or status."""
    db_member = get_organization_member(db, org_id, user_id)
    if not db_member:
        return None
    
    if role is not None:
        db_member.role = role
    if status is not None:
        db_member.status = status
    
    db_member.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_member)
    return db_member


def remove_organization_member(db: Session, org_id: str, user_id: str) -> bool:
    """Remove a member from an organization."""
    db_member = get_organization_member(db, org_id, user_id)
    if not db_member:
        return False
    
    db.delete(db_member)
    db.commit()
    return True


def get_user_role_in_organization(
    db: Session, 
    org_id: str, 
    user_id: str
) -> Optional[OrgRole]:
    """Get a user's role in an organization."""
    member = get_organization_member(db, org_id, user_id)
    return member.role if member else None


def is_user_org_admin(db: Session, org_id: str, user_id: str) -> bool:
    """Check if user is owner or admin of organization."""
    role = get_user_role_in_organization(db, org_id, user_id)
    return role in [OrgRole.OWNER, OrgRole.ADMIN]


# ============================================================================
# Organization Invites
# ============================================================================

def create_organization_invite(
    db: Session,
    org_id: str,
    invite_data: OrganizationInviteCreate,
    invited_by: str,
    expires_in_days: int = 7
) -> OrganizationInvite:
    """Create an invitation to join an organization."""
    token = secrets.token_urlsafe(32)
    
    db_invite = OrganizationInvite(
        organization_id=org_id,
        email=invite_data.email,
        role=invite_data.role,
        token=token,
        invited_by=invited_by,
        expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
    )
    db.add(db_invite)
    db.commit()
    db.refresh(db_invite)
    return db_invite


def get_organization_invite_by_token(
    db: Session, 
    token: str
) -> Optional[OrganizationInvite]:
    """Get an invite by its token."""
    return (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.token == token)
        .first()
    )


def accept_organization_invite(
    db: Session, 
    invite: OrganizationInvite, 
    user_id: str
) -> OrganizationMember:
    """Accept an organization invite and become a member."""
    # Mark invite as accepted
    invite.accepted_at = datetime.utcnow()
    
    # Add user as member
    db_member = add_organization_member(
        db,
        invite.organization_id,
        user_id,
        role=invite.role,
        invited_by=invite.invited_by
    )
    
    db.commit()
    return db_member


def get_pending_invites_for_email(
    db: Session, 
    email: str
) -> List[OrganizationInvite]:
    """Get all pending invites for an email address."""
    return (
        db.query(OrganizationInvite)
        .filter(
            OrganizationInvite.email == email,
            OrganizationInvite.accepted_at.is_(None),
            OrganizationInvite.expires_at > datetime.utcnow()
        )
        .all()
    )
