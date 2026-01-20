"""CRUD operations for Generated App entities."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from database.models import GeneratedApp, AppStatus
from schemas.generated_app import GeneratedAppCreate, GeneratedAppUpdate


def get_generated_app(db: Session, app_id: str) -> Optional[GeneratedApp]:
    """Get generated app by ID."""
    return db.query(GeneratedApp).filter(GeneratedApp.id == app_id).first()


def get_generated_app_by_safe_name(db: Session, safe_name: str) -> Optional[GeneratedApp]:
    """Get generated app by safe name."""
    return db.query(GeneratedApp).filter(GeneratedApp.safe_name == safe_name).first()


def get_generated_apps_by_project(
    db: Session, 
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[GeneratedApp]:
    """Get all generated apps for a project."""
    return (
        db.query(GeneratedApp)
        .filter(GeneratedApp.project_id == project_id)
        .order_by(GeneratedApp.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_running_apps(db: Session) -> List[GeneratedApp]:
    """Get all currently running apps."""
    return (
        db.query(GeneratedApp)
        .filter(GeneratedApp.status == AppStatus.RUNNING)
        .all()
    )


def create_generated_app(
    db: Session, 
    project_id: str,
    app_data: GeneratedAppCreate
) -> GeneratedApp:
    """Create a new generated app record."""
    db_app = GeneratedApp(
        project_id=project_id,
        safe_name=app_data.safe_name,
        project_path=app_data.project_path,
        frontend_port=app_data.frontend_port,
        backend_port=app_data.backend_port,
        preview_url=app_data.preview_url,
        status=app_data.status,
        docker_compose=app_data.docker_compose,
        frontend_files=app_data.frontend_files,
        backend_files=app_data.backend_files,
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


def update_generated_app(
    db: Session, 
    app_id: str, 
    app_data: GeneratedAppUpdate
) -> Optional[GeneratedApp]:
    """Update a generated app."""
    db_app = get_generated_app(db, app_id)
    if not db_app:
        return None
    
    update_data = app_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_app, field, value)
    
    db_app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_app)
    return db_app


def update_app_status(
    db: Session,
    app_id: str,
    status: AppStatus,
    error_log: Optional[str] = None
) -> Optional[GeneratedApp]:
    """Update app status with optional error log."""
    db_app = get_generated_app(db, app_id)
    if not db_app:
        return None
    
    db_app.status = status
    
    if status == AppStatus.RUNNING:
        db_app.started_at = datetime.utcnow()
    elif status == AppStatus.STOPPED:
        db_app.stopped_at = datetime.utcnow()
    elif status == AppStatus.ERROR and error_log:
        db_app.error_log = error_log
    
    db_app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_app)
    return db_app


def delete_generated_app(db: Session, app_id: str) -> bool:
    """Delete a generated app record."""
    db_app = get_generated_app(db, app_id)
    if not db_app:
        return False
    
    db.delete(db_app)
    db.commit()
    return True
