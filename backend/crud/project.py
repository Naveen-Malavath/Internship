"""CRUD operations for Project entities."""
import re
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Project, Feature, Story, Design, ProjectStatus
from schemas.project import ProjectCreate, ProjectUpdate


def slugify_key(text: str) -> str:
    """Convert text to URL-safe key."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text[:100]


def get_project(db: Session, project_id: str) -> Optional[Project]:
    """Get project by ID."""
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_with_counts(db: Session, project_id: str) -> Optional[dict]:
    """Get project with feature, story, and design counts."""
    project = get_project(db, project_id)
    if not project:
        return None
    
    feature_count = db.query(func.count(Feature.id)).filter(Feature.project_id == project_id).scalar()
    story_count = db.query(func.count(Story.id)).filter(Story.project_id == project_id).scalar()
    design_count = db.query(func.count(Design.id)).filter(Design.project_id == project_id).scalar()
    
    return {
        "project": project,
        "feature_count": feature_count,
        "story_count": story_count,
        "design_count": design_count,
    }


def get_projects_by_organization(
    db: Session, 
    org_id: str,
    status: Optional[ProjectStatus] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """Get all projects for an organization."""
    query = db.query(Project).filter(Project.organization_id == org_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    return query.order_by(Project.updated_at.desc()).offset(skip).limit(limit).all()


def get_project_count_by_organization(
    db: Session, 
    org_id: str,
    status: Optional[ProjectStatus] = None
) -> int:
    """Get count of projects for an organization."""
    query = db.query(func.count(Project.id)).filter(Project.organization_id == org_id)
    
    if status:
        query = query.filter(Project.status == status)
    
    return query.scalar()


def create_project(
    db: Session, 
    org_id: str,
    creator_id: str,
    project_data: ProjectCreate
) -> Project:
    """Create a new project."""
    # Generate key if not provided
    key = project_data.key or slugify_key(project_data.name)
    
    # Ensure key is unique within organization
    base_key = key
    counter = 1
    while db.query(Project).filter(
        Project.organization_id == org_id,
        Project.key == key
    ).first():
        key = f"{base_key}-{counter}"
        counter += 1
    
    db_project = Project(
        organization_id=org_id,
        created_by=creator_id,
        name=project_data.name,
        key=key,
        industry=project_data.industry,
        team_size=project_data.team_size,
        executive_summary=project_data.executive_summary,
        prompt_summary=project_data.prompt_summary,
        final_prompt=project_data.final_prompt,
        risk_highlights=project_data.risk_highlights,
        generated_risks=project_data.generated_risks,
        settings=project_data.settings,
        extra_data=project_data.extra_data,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def update_project(
    db: Session, 
    project_id: str, 
    project_data: ProjectUpdate
) -> Optional[Project]:
    """Update a project."""
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db_project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: str) -> bool:
    """Delete a project (cascades to features, stories, etc.)."""
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    
    db.delete(db_project)
    db.commit()
    return True


def check_project_access(
    db: Session, 
    project_id: str, 
    org_id: str
) -> bool:
    """Check if a project belongs to an organization."""
    return db.query(Project).filter(
        Project.id == project_id,
        Project.organization_id == org_id
    ).first() is not None
