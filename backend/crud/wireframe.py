"""CRUD operations for Wireframe entities."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import WireframePage, WireframeComponent, WireframeComponentType, DesignStatus
from schemas.wireframe import (
    WireframePageCreate, WireframePageUpdate,
    WireframeComponentCreate
)


# ============================================================================
# Wireframe Pages
# ============================================================================

def get_wireframe_page(db: Session, page_id: str) -> Optional[WireframePage]:
    """Get wireframe page by ID."""
    return db.query(WireframePage).filter(WireframePage.id == page_id).first()


def get_wireframe_pages_by_project(
    db: Session, 
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[WireframePage]:
    """Get all wireframe pages for a project."""
    return (
        db.query(WireframePage)
        .filter(WireframePage.project_id == project_id)
        .order_by(WireframePage.order_index, WireframePage.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_wireframe_page_count_by_project(db: Session, project_id: str) -> int:
    """Get count of wireframe pages for a project."""
    return db.query(func.count(WireframePage.id)).filter(
        WireframePage.project_id == project_id
    ).scalar()


def create_wireframe_page(
    db: Session, 
    project_id: str,
    page_data: WireframePageCreate
) -> WireframePage:
    """Create a new wireframe page."""
    # Get next order index
    max_order = db.query(func.max(WireframePage.order_index)).filter(
        WireframePage.project_id == project_id
    ).scalar() or -1
    
    db_page = WireframePage(
        project_id=project_id,
        page_name=page_data.page_name,
        page_type=page_data.page_type,
        html_content=page_data.html_content,
        description=page_data.description,
        order_index=page_data.order_index if page_data.order_index > 0 else max_order + 1,
        status=page_data.status,
    )
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page


def create_wireframe_pages_bulk(
    db: Session,
    project_id: str,
    pages_data: List[WireframePageCreate]
) -> List[WireframePage]:
    """Create multiple wireframe pages at once."""
    max_order = db.query(func.max(WireframePage.order_index)).filter(
        WireframePage.project_id == project_id
    ).scalar() or -1
    
    db_pages = []
    for i, page_data in enumerate(pages_data):
        db_page = WireframePage(
            project_id=project_id,
            page_name=page_data.page_name,
            page_type=page_data.page_type,
            html_content=page_data.html_content,
            description=page_data.description,
            order_index=max_order + i + 1,
            status=page_data.status,
        )
        db.add(db_page)
        db_pages.append(db_page)
    
    db.commit()
    for p in db_pages:
        db.refresh(p)
    
    return db_pages


def update_wireframe_page(
    db: Session, 
    page_id: str, 
    page_data: WireframePageUpdate
) -> Optional[WireframePage]:
    """Update a wireframe page."""
    db_page = get_wireframe_page(db, page_id)
    if not db_page:
        return None
    
    update_data = page_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_page, field, value)
    
    db_page.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_page)
    return db_page


def delete_wireframe_page(db: Session, page_id: str) -> bool:
    """Delete a wireframe page."""
    db_page = get_wireframe_page(db, page_id)
    if not db_page:
        return False
    
    db.delete(db_page)
    db.commit()
    return True


def delete_wireframe_pages_by_project(db: Session, project_id: str) -> int:
    """Delete all wireframe pages for a project."""
    count = db.query(WireframePage).filter(WireframePage.project_id == project_id).delete()
    db.commit()
    return count


# ============================================================================
# Wireframe Components
# ============================================================================

def get_wireframe_component(
    db: Session, 
    project_id: str, 
    component_type: WireframeComponentType
) -> Optional[WireframeComponent]:
    """Get wireframe component by project and type."""
    return (
        db.query(WireframeComponent)
        .filter(
            WireframeComponent.project_id == project_id,
            WireframeComponent.component_type == component_type
        )
        .first()
    )


def get_wireframe_components_by_project(
    db: Session, 
    project_id: str
) -> List[WireframeComponent]:
    """Get all wireframe components for a project."""
    return (
        db.query(WireframeComponent)
        .filter(WireframeComponent.project_id == project_id)
        .all()
    )


def create_or_update_wireframe_component(
    db: Session,
    project_id: str,
    component_type: WireframeComponentType,
    html_content: str
) -> WireframeComponent:
    """Create or update a wireframe component."""
    db_component = get_wireframe_component(db, project_id, component_type)
    
    if db_component:
        db_component.html_content = html_content
        db_component.updated_at = datetime.utcnow()
    else:
        db_component = WireframeComponent(
            project_id=project_id,
            component_type=component_type,
            html_content=html_content,
        )
        db.add(db_component)
    
    db.commit()
    db.refresh(db_component)
    return db_component
