"""
Design management router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, DesignType as DBDesignType, DesignStatus as DBDesignStatus
from routers.auth import get_current_user
from routers.projects import require_project_access
from schemas.design import (
    DesignCreate, DesignUpdate, DesignResponse, DesignListResponse,
    DesignType, DesignStatus
)
from crud.design import (
    get_design, get_designs_by_project, get_design_by_type,
    create_design, create_or_update_design, update_design, delete_design
)

router = APIRouter(
    prefix="/api/organizations/{org_id}/projects/{project_id}/designs",
    tags=["Designs"]
)


@router.get("/", response_model=DesignListResponse)
async def list_designs(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all designs for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    designs = get_designs_by_project(db, project_id)
    
    return DesignListResponse(
        designs=[
            DesignResponse(
                id=d.id,
                project_id=d.project_id,
                design_type=DesignType(d.design_type.value),
                diagram=d.diagram,
                summary=d.summary,
                version=d.version,
                status=DesignStatus(d.status.value),
                tokens_used=d.tokens_used or {},
                error_message=d.error_message,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in designs
        ],
        count=len(designs),
    )


@router.get("/{design_type}", response_model=DesignResponse)
async def get_design_by_type_endpoint(
    org_id: str,
    project_id: str,
    design_type: DesignType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific design by type."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    design = get_design_by_type(db, project_id, DBDesignType(design_type.value))
    if not design:
        raise HTTPException(status_code=404, detail=f"Design {design_type.value} not found")
    
    return DesignResponse(
        id=design.id,
        project_id=design.project_id,
        design_type=DesignType(design.design_type.value),
        diagram=design.diagram,
        summary=design.summary,
        version=design.version,
        status=DesignStatus(design.status.value),
        tokens_used=design.tokens_used or {},
        error_message=design.error_message,
        created_at=design.created_at,
        updated_at=design.updated_at,
    )


@router.put("/{design_type}", response_model=DesignResponse)
async def save_design(
    org_id: str,
    project_id: str,
    design_type: DesignType,
    design_data: DesignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a design by type."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    design = create_or_update_design(
        db,
        project_id,
        DBDesignType(design_type.value),
        diagram=design_data.diagram,
        summary=design_data.summary,
        status=DBDesignStatus(design_data.status.value) if design_data.status else DBDesignStatus.COMPLETED,
        tokens_used=design_data.tokens_used,
        error_message=design_data.error_message,
    )
    
    return DesignResponse(
        id=design.id,
        project_id=design.project_id,
        design_type=DesignType(design.design_type.value),
        diagram=design.diagram,
        summary=design.summary,
        version=design.version,
        status=DesignStatus(design.status.value),
        tokens_used=design.tokens_used or {},
        error_message=design.error_message,
        created_at=design.created_at,
        updated_at=design.updated_at,
    )


@router.delete("/{design_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_design_endpoint(
    org_id: str,
    project_id: str,
    design_type: DesignType,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a design by type."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    design = get_design_by_type(db, project_id, DBDesignType(design_type.value))
    if not design:
        raise HTTPException(status_code=404, detail=f"Design {design_type.value} not found")
    
    delete_design(db, design.id)
