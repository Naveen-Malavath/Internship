"""
Wireframe management router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, WireframeComponentType as DBComponentType, DesignStatus as DBDesignStatus
from routers.auth import get_current_user
from routers.projects import require_project_access
from schemas.wireframe import (
    WireframePageCreate, WireframePageUpdate, WireframePageResponse,
    WireframeComponentCreate, WireframeComponentResponse,
    WireframeDataResponse, WireframeComponentType, DesignStatus
)
from crud.wireframe import (
    get_wireframe_page, get_wireframe_pages_by_project, get_wireframe_page_count_by_project,
    create_wireframe_page, create_wireframe_pages_bulk,
    update_wireframe_page, delete_wireframe_page,
    get_wireframe_components_by_project, create_or_update_wireframe_component
)

router = APIRouter(
    prefix="/api/organizations/{org_id}/projects/{project_id}/wireframes",
    tags=["Wireframes"]
)


@router.get("/", response_model=WireframeDataResponse)
async def get_wireframe_data(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wireframe pages and components for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    pages = get_wireframe_pages_by_project(db, project_id)
    components = get_wireframe_components_by_project(db, project_id)
    
    return WireframeDataResponse(
        pages=[
            WireframePageResponse(
                id=p.id,
                project_id=p.project_id,
                page_name=p.page_name,
                page_type=p.page_type,
                html_content=p.html_content,
                description=p.description,
                order_index=p.order_index,
                status=DesignStatus(p.status.value),
                error_message=p.error_message,
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
            for p in pages
        ],
        components=[
            WireframeComponentResponse(
                id=c.id,
                project_id=c.project_id,
                component_type=WireframeComponentType(c.component_type.value),
                html_content=c.html_content,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in components
        ],
        total_pages=len(pages),
    )


@router.get("/pages", response_model=List[WireframePageResponse])
async def list_wireframe_pages(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wireframe pages for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    pages = get_wireframe_pages_by_project(db, project_id)
    
    return [
        WireframePageResponse(
            id=p.id,
            project_id=p.project_id,
            page_name=p.page_name,
            page_type=p.page_type,
            html_content=p.html_content,
            description=p.description,
            order_index=p.order_index,
            status=DesignStatus(p.status.value),
            error_message=p.error_message,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in pages
    ]


@router.post("/pages", response_model=WireframePageResponse, status_code=status.HTTP_201_CREATED)
async def create_wireframe_page_endpoint(
    org_id: str,
    project_id: str,
    page_data: WireframePageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new wireframe page."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    page = create_wireframe_page(db, project_id, page_data)
    
    return WireframePageResponse(
        id=page.id,
        project_id=page.project_id,
        page_name=page.page_name,
        page_type=page.page_type,
        html_content=page.html_content,
        description=page.description,
        order_index=page.order_index,
        status=DesignStatus(page.status.value),
        error_message=page.error_message,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.post("/pages/bulk", response_model=List[WireframePageResponse], status_code=status.HTTP_201_CREATED)
async def create_wireframe_pages_bulk_endpoint(
    org_id: str,
    project_id: str,
    pages_data: List[WireframePageCreate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple wireframe pages at once."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    pages = create_wireframe_pages_bulk(db, project_id, pages_data)
    
    return [
        WireframePageResponse(
            id=p.id,
            project_id=p.project_id,
            page_name=p.page_name,
            page_type=p.page_type,
            html_content=p.html_content,
            description=p.description,
            order_index=p.order_index,
            status=DesignStatus(p.status.value),
            error_message=p.error_message,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )
        for p in pages
    ]


@router.get("/pages/{page_id}", response_model=WireframePageResponse)
async def get_wireframe_page_endpoint(
    org_id: str,
    project_id: str,
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a wireframe page."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    page = get_wireframe_page(db, page_id)
    if not page or page.project_id != project_id:
        raise HTTPException(status_code=404, detail="Wireframe page not found")
    
    return WireframePageResponse(
        id=page.id,
        project_id=page.project_id,
        page_name=page.page_name,
        page_type=page.page_type,
        html_content=page.html_content,
        description=page.description,
        order_index=page.order_index,
        status=DesignStatus(page.status.value),
        error_message=page.error_message,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.patch("/pages/{page_id}", response_model=WireframePageResponse)
async def update_wireframe_page_endpoint(
    org_id: str,
    project_id: str,
    page_id: str,
    page_data: WireframePageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a wireframe page."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_wireframe_page(db, page_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Wireframe page not found")
    
    page = update_wireframe_page(db, page_id, page_data)
    
    return WireframePageResponse(
        id=page.id,
        project_id=page.project_id,
        page_name=page.page_name,
        page_type=page.page_type,
        html_content=page.html_content,
        description=page.description,
        order_index=page.order_index,
        status=DesignStatus(page.status.value),
        error_message=page.error_message,
        created_at=page.created_at,
        updated_at=page.updated_at,
    )


@router.delete("/pages/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wireframe_page_endpoint(
    org_id: str,
    project_id: str,
    page_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a wireframe page."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_wireframe_page(db, page_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Wireframe page not found")
    
    delete_wireframe_page(db, page_id)


# ============================================================================
# Components
# ============================================================================

@router.get("/components", response_model=List[WireframeComponentResponse])
async def list_wireframe_components(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all wireframe components for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    components = get_wireframe_components_by_project(db, project_id)
    
    return [
        WireframeComponentResponse(
            id=c.id,
            project_id=c.project_id,
            component_type=WireframeComponentType(c.component_type.value),
            html_content=c.html_content,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in components
    ]


@router.put("/components/{component_type}", response_model=WireframeComponentResponse)
async def save_wireframe_component(
    org_id: str,
    project_id: str,
    component_type: WireframeComponentType,
    component_data: WireframeComponentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a wireframe component."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    component = create_or_update_wireframe_component(
        db,
        project_id,
        DBComponentType(component_type.value),
        component_data.html_content,
    )
    
    return WireframeComponentResponse(
        id=component.id,
        project_id=component.project_id,
        component_type=WireframeComponentType(component.component_type.value),
        html_content=component.html_content,
        created_at=component.created_at,
        updated_at=component.updated_at,
    )
