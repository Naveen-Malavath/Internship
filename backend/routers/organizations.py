"""
Organization management router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, OrgRole
from routers.auth import get_current_user
from schemas.organization import (
    OrganizationCreate, OrganizationUpdate, OrganizationResponse,
    OrganizationWithMembers, OrganizationMemberResponse,
    OrganizationInviteCreate, OrganizationInviteResponse,
    OrgRole as OrgRoleSchema
)
from crud.organization import (
    get_organization, get_organization_by_slug, get_user_organizations,
    create_organization, update_organization, delete_organization,
    get_organization_member, get_organization_members,
    add_organization_member, update_organization_member, remove_organization_member,
    create_organization_invite, is_user_org_admin, get_user_role_in_organization
)
from crud.project import get_project_count_by_organization

router = APIRouter(prefix="/api/organizations", tags=["Organizations"])


def require_org_member(
    db: Session,
    org_id: str,
    user_id: str,
    min_role: Optional[OrgRole] = None
) -> OrgRole:
    """Check if user is a member of the organization with required role."""
    role = get_user_role_in_organization(db, org_id, user_id)
    
    if not role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )
    
    if min_role:
        role_hierarchy = [OrgRole.VIEWER, OrgRole.MEMBER, OrgRole.ADMIN, OrgRole.OWNER]
        if role_hierarchy.index(role) < role_hierarchy.index(min_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires {min_role.value} role or higher",
            )
    
    return role


@router.get("/", response_model=List[OrganizationResponse])
async def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all organizations the current user belongs to."""
    orgs = get_user_organizations(db, current_user.id)
    return orgs


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_organization(
    org_data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization. The creator becomes the owner."""
    org = create_organization(db, org_data, current_user.id)
    return org


@router.get("/{org_id}", response_model=OrganizationWithMembers)
async def get_organization_details(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization details including members."""
    require_org_member(db, org_id, current_user.id)
    
    org = get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    members = get_organization_members(db, org_id)
    project_count = get_project_count_by_organization(db, org_id)
    
    # Build member responses with user info
    member_responses = []
    for member in members:
        member_responses.append(OrganizationMemberResponse(
            id=member.id,
            organization_id=member.organization_id,
            user_id=member.user_id,
            role=OrgRoleSchema(member.role.value),
            status=member.status,
            invited_by=member.invited_by,
            joined_at=member.joined_at,
            created_at=member.created_at,
            user_email=member.user.email if member.user else None,
            user_name=member.user.name if member.user else None,
            user_avatar_url=member.user.avatar_url if member.user else None,
        ))
    
    return OrganizationWithMembers(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        settings=org.settings,
        plan=org.plan,
        created_by=org.created_by,
        created_at=org.created_at,
        updated_at=org.updated_at,
        members=member_responses,
        member_count=len(members),
        project_count=project_count,
    )


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization_details(
    org_id: str,
    org_data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization details. Requires admin or owner role."""
    require_org_member(db, org_id, current_user.id, min_role=OrgRole.ADMIN)
    
    org = update_organization(db, org_id, org_data)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization_endpoint(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an organization. Requires owner role."""
    require_org_member(db, org_id, current_user.id, min_role=OrgRole.OWNER)
    
    if not delete_organization(db, org_id):
        raise HTTPException(status_code=404, detail="Organization not found")


# ============================================================================
# Members
# ============================================================================

@router.get("/{org_id}/members", response_model=List[OrganizationMemberResponse])
async def list_organization_members(
    org_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all members of an organization."""
    require_org_member(db, org_id, current_user.id)
    
    members = get_organization_members(db, org_id)
    
    return [
        OrganizationMemberResponse(
            id=m.id,
            organization_id=m.organization_id,
            user_id=m.user_id,
            role=OrgRoleSchema(m.role.value),
            status=m.status,
            invited_by=m.invited_by,
            joined_at=m.joined_at,
            created_at=m.created_at,
            user_email=m.user.email if m.user else None,
            user_name=m.user.name if m.user else None,
            user_avatar_url=m.user.avatar_url if m.user else None,
        )
        for m in members
    ]


@router.patch("/{org_id}/members/{user_id}", response_model=OrganizationMemberResponse)
async def update_member_role(
    org_id: str,
    user_id: str,
    role: OrgRoleSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member's role. Requires admin or owner role."""
    current_role = require_org_member(db, org_id, current_user.id, min_role=OrgRole.ADMIN)
    
    # Can't change owner role unless you're also owner
    target_member = get_organization_member(db, org_id, user_id)
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    if target_member.role == OrgRole.OWNER and current_role != OrgRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can change owner's role",
        )
    
    # Can't promote to owner unless you're owner
    if role == OrgRoleSchema.OWNER and current_role != OrgRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can promote to owner",
        )
    
    member = update_organization_member(db, org_id, user_id, role=OrgRole(role.value))
    
    return OrganizationMemberResponse(
        id=member.id,
        organization_id=member.organization_id,
        user_id=member.user_id,
        role=OrgRoleSchema(member.role.value),
        status=member.status,
        invited_by=member.invited_by,
        joined_at=member.joined_at,
        created_at=member.created_at,
        user_email=member.user.email if member.user else None,
        user_name=member.user.name if member.user else None,
        user_avatar_url=member.user.avatar_url if member.user else None,
    )


@router.delete("/{org_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    org_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a member from the organization. Requires admin or owner role."""
    current_role = require_org_member(db, org_id, current_user.id, min_role=OrgRole.ADMIN)
    
    # Check target member
    target_member = get_organization_member(db, org_id, user_id)
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Can't remove owner
    if target_member.role == OrgRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove the owner. Transfer ownership first.",
        )
    
    # Admin can only remove members and viewers
    if current_role == OrgRole.ADMIN and target_member.role == OrgRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot remove other admins",
        )
    
    remove_organization_member(db, org_id, user_id)


# ============================================================================
# Invites
# ============================================================================

@router.post("/{org_id}/invites", response_model=OrganizationInviteResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    org_id: str,
    invite_data: OrganizationInviteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite a new member to the organization. Requires admin or owner role."""
    require_org_member(db, org_id, current_user.id, min_role=OrgRole.ADMIN)
    
    # Check if already a member
    from crud.user import get_user_by_email
    existing_user = get_user_by_email(db, invite_data.email)
    if existing_user:
        existing_member = get_organization_member(db, org_id, existing_user.id)
        if existing_member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization",
            )
    
    org = get_organization(db, org_id)
    invite = create_organization_invite(db, org_id, invite_data, current_user.id)
    
    return OrganizationInviteResponse(
        id=invite.id,
        organization_id=invite.organization_id,
        email=invite.email,
        role=OrgRoleSchema(invite.role.value),
        token=invite.token,
        invited_by=invite.invited_by,
        expires_at=invite.expires_at,
        accepted_at=invite.accepted_at,
        created_at=invite.created_at,
        organization_name=org.name if org else None,
    )
