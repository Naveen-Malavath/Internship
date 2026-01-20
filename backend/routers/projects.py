"""
Project management router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, OrgRole, ProjectStatus
from routers.auth import get_current_user
from routers.organizations import require_org_member
from schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectStatus as ProjectStatusSchema
)
from crud.project import (
    get_project, get_project_with_counts, get_projects_by_organization,
    get_project_count_by_organization, create_project, update_project, delete_project,
    check_project_access
)
from crud.feature import get_feature_count_by_project
from crud.story import get_story_count_by_project

router = APIRouter(prefix="/api/organizations/{org_id}/projects", tags=["Projects"])


def require_project_access(
    db: Session,
    org_id: str,
    project_id: str,
    user_id: str,
    require_write: bool = False
) -> OrgRole:
    """Check if user can access the project."""
    role = require_org_member(db, org_id, user_id)
    
    # Check project belongs to org
    if not check_project_access(db, project_id, org_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in this organization",
        )
    
    # Viewers can only read
    if require_write and role == OrgRole.VIEWER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot modify projects",
        )
    
    return role


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    org_id: str,
    status: Optional[ProjectStatusSchema] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects for an organization."""
    require_org_member(db, org_id, current_user.id)
    
    skip = (page - 1) * page_size
    db_status = ProjectStatus(status.value) if status else None
    
    projects = get_projects_by_organization(db, org_id, status=db_status, skip=skip, limit=page_size)
    total = get_project_count_by_organization(db, org_id, status=db_status)
    
    # Add counts to each project
    project_responses = []
    for project in projects:
        feature_count = get_feature_count_by_project(db, project.id)
        story_count = get_story_count_by_project(db, project.id)
        
        project_responses.append(ProjectResponse(
            id=project.id,
            organization_id=project.organization_id,
            created_by=project.created_by,
            name=project.name,
            key=project.key,
            industry=project.industry,
            team_size=project.team_size,
            executive_summary=project.executive_summary,
            prompt_summary=project.prompt_summary,
            final_prompt=project.final_prompt,
            risk_highlights=project.risk_highlights or [],
            generated_risks=project.generated_risks,
            status=ProjectStatusSchema(project.status.value),
            settings=project.settings or {},
            extra_data=project.extra_data or {},
            created_at=project.created_at,
            updated_at=project.updated_at,
            feature_count=feature_count,
            story_count=story_count,
        ))
    
    return ProjectListResponse(
        projects=project_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    org_id: str,
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project. Requires member role or higher."""
    require_org_member(db, org_id, current_user.id, min_role=OrgRole.MEMBER)
    
    project = create_project(db, org_id, current_user.id, project_data)
    
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        created_by=project.created_by,
        name=project.name,
        key=project.key,
        industry=project.industry,
        team_size=project.team_size,
        executive_summary=project.executive_summary,
        prompt_summary=project.prompt_summary,
        final_prompt=project.final_prompt,
        risk_highlights=project.risk_highlights or [],
        generated_risks=project.generated_risks,
        status=ProjectStatusSchema(project.status.value),
        settings=project.settings or {},
        metadata=project.metadata or {},
        created_at=project.created_at,
        updated_at=project.updated_at,
        feature_count=0,
        story_count=0,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project_details(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details with counts."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    result = get_project_with_counts(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = result["project"]
    
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        created_by=project.created_by,
        name=project.name,
        key=project.key,
        industry=project.industry,
        team_size=project.team_size,
        executive_summary=project.executive_summary,
        prompt_summary=project.prompt_summary,
        final_prompt=project.final_prompt,
        risk_highlights=project.risk_highlights or [],
        generated_risks=project.generated_risks,
        status=ProjectStatusSchema(project.status.value),
        settings=project.settings or {},
        metadata=project.metadata or {},
        created_at=project.created_at,
        updated_at=project.updated_at,
        feature_count=result["feature_count"],
        story_count=result["story_count"],
        design_count=result["design_count"],
    )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_details(
    org_id: str,
    project_id: str,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project details."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    project = update_project(db, project_id, project_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    feature_count = get_feature_count_by_project(db, project.id)
    story_count = get_story_count_by_project(db, project.id)
    
    return ProjectResponse(
        id=project.id,
        organization_id=project.organization_id,
        created_by=project.created_by,
        name=project.name,
        key=project.key,
        industry=project.industry,
        team_size=project.team_size,
        executive_summary=project.executive_summary,
        prompt_summary=project.prompt_summary,
        final_prompt=project.final_prompt,
        risk_highlights=project.risk_highlights or [],
        generated_risks=project.generated_risks,
        status=ProjectStatusSchema(project.status.value),
        settings=project.settings or {},
        metadata=project.metadata or {},
        created_at=project.created_at,
        updated_at=project.updated_at,
        feature_count=feature_count,
        story_count=story_count,
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_endpoint(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project. Requires admin or owner role."""
    require_org_member(db, org_id, current_user.id, min_role=OrgRole.ADMIN)
    require_project_access(db, org_id, project_id, current_user.id)
    
    if not delete_project(db, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
