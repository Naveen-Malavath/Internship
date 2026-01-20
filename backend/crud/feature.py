"""CRUD operations for Feature entities."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Feature, Story
from schemas.feature import FeatureCreate, FeatureUpdate


def get_feature(db: Session, feature_id: str) -> Optional[Feature]:
    """Get feature by ID."""
    return db.query(Feature).filter(Feature.id == feature_id).first()


def get_feature_with_story_count(db: Session, feature_id: str) -> Optional[dict]:
    """Get feature with story count."""
    feature = get_feature(db, feature_id)
    if not feature:
        return None
    
    story_count = db.query(func.count(Story.id)).filter(Story.feature_id == feature_id).scalar()
    
    return {
        "feature": feature,
        "story_count": story_count,
    }


def get_features_by_project(
    db: Session, 
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Feature]:
    """Get all features for a project."""
    return (
        db.query(Feature)
        .filter(Feature.project_id == project_id)
        .order_by(Feature.order_index, Feature.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_feature_count_by_project(db: Session, project_id: str) -> int:
    """Get count of features for a project."""
    return db.query(func.count(Feature.id)).filter(Feature.project_id == project_id).scalar()


def create_feature(
    db: Session, 
    project_id: str,
    feature_data: FeatureCreate
) -> Feature:
    """Create a new feature."""
    # Get next order index
    max_order = db.query(func.max(Feature.order_index)).filter(
        Feature.project_id == project_id
    ).scalar() or -1
    
    db_feature = Feature(
        project_id=project_id,
        title=feature_data.title,
        reason=feature_data.reason,
        problem_statement=feature_data.problem_statement,
        business_objective=feature_data.business_objective,
        user_persona=feature_data.user_persona,
        acceptance_criteria=feature_data.acceptance_criteria,
        detailed_description=feature_data.detailed_description,
        success_metrics=feature_data.success_metrics,
        dependencies=feature_data.dependencies,
        order_index=feature_data.order_index if feature_data.order_index > 0 else max_order + 1,
        approved=feature_data.approved,
        custom_fields=feature_data.custom_fields,
    )
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature


def create_features_bulk(
    db: Session,
    project_id: str,
    features_data: List[FeatureCreate]
) -> List[Feature]:
    """Create multiple features at once."""
    # Get current max order index
    max_order = db.query(func.max(Feature.order_index)).filter(
        Feature.project_id == project_id
    ).scalar() or -1
    
    db_features = []
    for i, feature_data in enumerate(features_data):
        db_feature = Feature(
            project_id=project_id,
            title=feature_data.title,
            reason=feature_data.reason,
            problem_statement=feature_data.problem_statement,
            business_objective=feature_data.business_objective,
            user_persona=feature_data.user_persona,
            acceptance_criteria=feature_data.acceptance_criteria,
            detailed_description=feature_data.detailed_description,
            success_metrics=feature_data.success_metrics,
            dependencies=feature_data.dependencies,
            order_index=max_order + i + 1,
            approved=feature_data.approved,
            custom_fields=feature_data.custom_fields,
        )
        db.add(db_feature)
        db_features.append(db_feature)
    
    db.commit()
    for f in db_features:
        db.refresh(f)
    
    return db_features


def update_feature(
    db: Session, 
    feature_id: str, 
    feature_data: FeatureUpdate
) -> Optional[Feature]:
    """Update a feature."""
    db_feature = get_feature(db, feature_id)
    if not db_feature:
        return None
    
    update_data = feature_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feature, field, value)
    
    db_feature.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_feature)
    return db_feature


def delete_feature(db: Session, feature_id: str) -> bool:
    """Delete a feature (cascades to stories)."""
    db_feature = get_feature(db, feature_id)
    if not db_feature:
        return False
    
    db.delete(db_feature)
    db.commit()
    return True


def reorder_features(
    db: Session,
    project_id: str,
    feature_ids: List[str]
) -> List[Feature]:
    """Reorder features by providing new order of IDs."""
    features = []
    for i, feature_id in enumerate(feature_ids):
        feature = get_feature(db, feature_id)
        if feature and feature.project_id == project_id:
            feature.order_index = i
            features.append(feature)
    
    db.commit()
    return features
