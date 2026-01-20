"""
Generated App management router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, AppStatus as DBAppStatus
from routers.auth import get_current_user
from routers.projects import require_project_access
from schemas.generated_app import (
    GeneratedAppCreate, GeneratedAppUpdate, GeneratedAppResponse,
    GeneratedAppListResponse, AppStatus
)
from crud.generated_app import (
    get_generated_app, get_generated_app_by_safe_name,
    get_generated_apps_by_project,
    create_generated_app, update_generated_app, update_app_status,
    delete_generated_app
)

router = APIRouter(
    prefix="/api/organizations/{org_id}/projects/{project_id}/apps",
    tags=["Generated Apps"]
)


@router.get("/", response_model=GeneratedAppListResponse)
async def list_generated_apps(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all generated apps for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    apps = get_generated_apps_by_project(db, project_id)
    
    return GeneratedAppListResponse(
        apps=[
            GeneratedAppResponse(
                id=a.id,
                project_id=a.project_id,
                safe_name=a.safe_name,
                project_path=a.project_path,
                frontend_port=a.frontend_port,
                backend_port=a.backend_port,
                preview_url=a.preview_url,
                status=AppStatus(a.status.value),
                docker_compose=a.docker_compose,
                frontend_files=a.frontend_files or {},
                backend_files=a.backend_files or {},
                build_log=a.build_log,
                error_log=a.error_log,
                created_at=a.created_at,
                started_at=a.started_at,
                stopped_at=a.stopped_at,
                updated_at=a.updated_at,
            )
            for a in apps
        ],
        count=len(apps),
    )


@router.post("/", response_model=GeneratedAppResponse, status_code=status.HTTP_201_CREATED)
async def create_generated_app_endpoint(
    org_id: str,
    project_id: str,
    app_data: GeneratedAppCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new generated app record."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    # Check if safe_name already exists
    existing = get_generated_app_by_safe_name(db, app_data.safe_name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"App with safe_name '{app_data.safe_name}' already exists"
        )
    
    app = create_generated_app(db, project_id, app_data)
    
    return GeneratedAppResponse(
        id=app.id,
        project_id=app.project_id,
        safe_name=app.safe_name,
        project_path=app.project_path,
        frontend_port=app.frontend_port,
        backend_port=app.backend_port,
        preview_url=app.preview_url,
        status=AppStatus(app.status.value),
        docker_compose=app.docker_compose,
        frontend_files=app.frontend_files or {},
        backend_files=app.backend_files or {},
        build_log=app.build_log,
        error_log=app.error_log,
        created_at=app.created_at,
        started_at=app.started_at,
        stopped_at=app.stopped_at,
        updated_at=app.updated_at,
    )


@router.get("/{app_id}", response_model=GeneratedAppResponse)
async def get_generated_app_endpoint(
    org_id: str,
    project_id: str,
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a generated app."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    app = get_generated_app(db, app_id)
    if not app or app.project_id != project_id:
        raise HTTPException(status_code=404, detail="Generated app not found")
    
    return GeneratedAppResponse(
        id=app.id,
        project_id=app.project_id,
        safe_name=app.safe_name,
        project_path=app.project_path,
        frontend_port=app.frontend_port,
        backend_port=app.backend_port,
        preview_url=app.preview_url,
        status=AppStatus(app.status.value),
        docker_compose=app.docker_compose,
        frontend_files=app.frontend_files or {},
        backend_files=app.backend_files or {},
        build_log=app.build_log,
        error_log=app.error_log,
        created_at=app.created_at,
        started_at=app.started_at,
        stopped_at=app.stopped_at,
        updated_at=app.updated_at,
    )


@router.patch("/{app_id}", response_model=GeneratedAppResponse)
async def update_generated_app_endpoint(
    org_id: str,
    project_id: str,
    app_id: str,
    app_data: GeneratedAppUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a generated app."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_generated_app(db, app_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Generated app not found")
    
    app = update_generated_app(db, app_id, app_data)
    
    return GeneratedAppResponse(
        id=app.id,
        project_id=app.project_id,
        safe_name=app.safe_name,
        project_path=app.project_path,
        frontend_port=app.frontend_port,
        backend_port=app.backend_port,
        preview_url=app.preview_url,
        status=AppStatus(app.status.value),
        docker_compose=app.docker_compose,
        frontend_files=app.frontend_files or {},
        backend_files=app.backend_files or {},
        build_log=app.build_log,
        error_log=app.error_log,
        created_at=app.created_at,
        started_at=app.started_at,
        stopped_at=app.stopped_at,
        updated_at=app.updated_at,
    )


@router.patch("/{app_id}/status", response_model=GeneratedAppResponse)
async def update_app_status_endpoint(
    org_id: str,
    project_id: str,
    app_id: str,
    new_status: AppStatus,
    error_log: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update only the status of a generated app."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_generated_app(db, app_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Generated app not found")
    
    app = update_app_status(db, app_id, DBAppStatus(new_status.value), error_log)
    
    return GeneratedAppResponse(
        id=app.id,
        project_id=app.project_id,
        safe_name=app.safe_name,
        project_path=app.project_path,
        frontend_port=app.frontend_port,
        backend_port=app.backend_port,
        preview_url=app.preview_url,
        status=AppStatus(app.status.value),
        docker_compose=app.docker_compose,
        frontend_files=app.frontend_files or {},
        backend_files=app.backend_files or {},
        build_log=app.build_log,
        error_log=app.error_log,
        created_at=app.created_at,
        started_at=app.started_at,
        stopped_at=app.stopped_at,
        updated_at=app.updated_at,
    )


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_generated_app_endpoint(
    org_id: str,
    project_id: str,
    app_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a generated app record."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_generated_app(db, app_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Generated app not found")
    
    delete_generated_app(db, app_id)
