"""CRUD operations for Story entities."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from database.models import Story, Feature
from schemas.story import StoryCreate, StoryUpdate


def get_story(db: Session, story_id: str) -> Optional[Story]:
    """Get story by ID."""
    return db.query(Story).filter(Story.id == story_id).first()


def get_stories_by_project(
    db: Session, 
    project_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Story]:
    """Get all stories for a project."""
    return (
        db.query(Story)
        .filter(Story.project_id == project_id)
        .order_by(Story.feature_id, Story.order_index, Story.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_stories_by_feature(
    db: Session, 
    feature_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[Story]:
    """Get all stories for a feature."""
    return (
        db.query(Story)
        .filter(Story.feature_id == feature_id)
        .order_by(Story.order_index, Story.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_story_count_by_project(db: Session, project_id: str) -> int:
    """Get count of stories for a project."""
    return db.query(func.count(Story.id)).filter(Story.project_id == project_id).scalar()


def get_story_count_by_feature(db: Session, feature_id: str) -> int:
    """Get count of stories for a feature."""
    return db.query(func.count(Story.id)).filter(Story.feature_id == feature_id).scalar()


def create_story(
    db: Session, 
    project_id: str,
    story_data: StoryCreate
) -> Story:
    """Create a new story."""
    # Get next order index for this feature
    max_order = db.query(func.max(Story.order_index)).filter(
        Story.feature_id == story_data.feature_id
    ).scalar() or -1
    
    # Get feature title for reference
    feature = db.query(Feature).filter(Feature.id == story_data.feature_id).first()
    
    db_story = Story(
        project_id=project_id,
        feature_id=story_data.feature_id,
        title=story_data.title,
        description=story_data.description,
        feature_ref=story_data.feature_ref or (feature.title if feature else None),
        feature_context=story_data.feature_context,
        order_index=story_data.order_index if story_data.order_index > 0 else max_order + 1,
        approved=story_data.approved,
        custom_fields=story_data.custom_fields,
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story


def create_stories_bulk(
    db: Session,
    project_id: str,
    stories_data: List[StoryCreate]
) -> List[Story]:
    """Create multiple stories at once."""
    db_stories = []
    
    # Group by feature to handle order indices
    feature_orders = {}
    
    for story_data in stories_data:
        feature_id = story_data.feature_id
        
        if feature_id not in feature_orders:
            max_order = db.query(func.max(Story.order_index)).filter(
                Story.feature_id == feature_id
            ).scalar() or -1
            feature_orders[feature_id] = max_order
        
        feature_orders[feature_id] += 1
        
        # Get feature for reference
        feature = db.query(Feature).filter(Feature.id == feature_id).first()
        
        db_story = Story(
            project_id=project_id,
            feature_id=feature_id,
            title=story_data.title,
            description=story_data.description,
            feature_ref=story_data.feature_ref or (feature.title if feature else None),
            feature_context=story_data.feature_context,
            order_index=feature_orders[feature_id],
            approved=story_data.approved,
            custom_fields=story_data.custom_fields,
        )
        db.add(db_story)
        db_stories.append(db_story)
    
    db.commit()
    for s in db_stories:
        db.refresh(s)
    
    return db_stories


def update_story(
    db: Session, 
    story_id: str, 
    story_data: StoryUpdate
) -> Optional[Story]:
    """Update a story."""
    db_story = get_story(db, story_id)
    if not db_story:
        return None
    
    update_data = story_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_story, field, value)
    
    db_story.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_story)
    return db_story


def delete_story(db: Session, story_id: str) -> bool:
    """Delete a story."""
    db_story = get_story(db, story_id)
    if not db_story:
        return False
    
    db.delete(db_story)
    db.commit()
    return True


def reorder_stories(
    db: Session,
    feature_id: str,
    story_ids: List[str]
) -> List[Story]:
    """Reorder stories within a feature."""
    stories = []
    for i, story_id in enumerate(story_ids):
        story = get_story(db, story_id)
        if story and story.feature_id == feature_id:
            story.order_index = i
            stories.append(story)
    
    db.commit()
    return stories
