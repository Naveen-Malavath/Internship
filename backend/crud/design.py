"""CRUD operations for Design entities."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from database.models import Design, DesignType, DesignStatus
from schemas.design import DesignCreate, DesignUpdate


def get_design(db: Session, design_id: str) -> Optional[Design]:
    """Get design by ID."""
    return db.query(Design).filter(Design.id == design_id).first()


def get_design_by_type(
    db: Session, 
    project_id: str, 
    design_type: DesignType
) -> Optional[Design]:
    """Get design by project and type."""
    return (
        db.query(Design)
        .filter(
            Design.project_id == project_id,
            Design.design_type == design_type
        )
        .first()
    )


def get_designs_by_project(db: Session, project_id: str) -> List[Design]:
    """Get all designs for a project."""
    return (
        db.query(Design)
        .filter(Design.project_id == project_id)
        .order_by(Design.design_type)
        .all()
    )


def create_design(
    db: Session, 
    project_id: str,
    design_data: DesignCreate
) -> Design:
    """Create a new design."""
    db_design = Design(
        project_id=project_id,
        design_type=design_data.design_type,
        diagram=design_data.diagram,
        summary=design_data.summary,
        status=design_data.status,
        tokens_used=design_data.tokens_used,
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)
    return db_design


def create_or_update_design(
    db: Session,
    project_id: str,
    design_type: DesignType,
    diagram: Optional[str] = None,
    summary: Optional[str] = None,
    status: DesignStatus = DesignStatus.COMPLETED,
    tokens_used: Optional[dict] = None,
    error_message: Optional[str] = None
) -> Design:
    """Create or update a design by type."""
    db_design = get_design_by_type(db, project_id, design_type)
    
    if db_design:
        # Update existing
        if diagram is not None:
            db_design.diagram = diagram
        if summary is not None:
            db_design.summary = summary
        if status is not None:
            db_design.status = status
        if tokens_used is not None:
            db_design.tokens_used = tokens_used
        if error_message is not None:
            db_design.error_message = error_message
        db_design.version += 1
        db_design.updated_at = datetime.utcnow()
    else:
        # Create new
        db_design = Design(
            project_id=project_id,
            design_type=design_type,
            diagram=diagram,
            summary=summary,
            status=status,
            tokens_used=tokens_used or {},
            error_message=error_message,
        )
        db.add(db_design)
    
    db.commit()
    db.refresh(db_design)
    return db_design


def update_design(
    db: Session, 
    design_id: str, 
    design_data: DesignUpdate
) -> Optional[Design]:
    """Update a design."""
    db_design = get_design(db, design_id)
    if not db_design:
        return None
    
    update_data = design_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_design, field, value)
    
    db_design.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_design)
    return db_design


def delete_design(db: Session, design_id: str) -> bool:
    """Delete a design."""
    db_design = get_design(db, design_id)
    if not db_design:
        return False
    
    db.delete(db_design)
    db.commit()
    return True


def delete_designs_by_project(db: Session, project_id: str) -> int:
    """Delete all designs for a project."""
    count = db.query(Design).filter(Design.project_id == project_id).delete()
    db.commit()
    return count
