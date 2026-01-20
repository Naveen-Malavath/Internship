"""
Story management router.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User
from routers.auth import get_current_user
from routers.projects import require_project_access
from schemas.story import (
    StoryCreate, StoryUpdate, StoryResponse,
    StoryBulkCreate, StoryBulkResponse
)
from crud.story import (
    get_story, get_stories_by_project, get_stories_by_feature,
    create_story, create_stories_bulk, update_story, delete_story,
    reorder_stories
)
from crud.feature import get_feature

router = APIRouter(
    prefix="/api/organizations/{org_id}/projects/{project_id}/stories",
    tags=["Stories"]
)


@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    org_id: str,
    project_id: str,
    feature_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all stories for a project or filter by feature."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    if feature_id:
        stories = get_stories_by_feature(db, feature_id)
    else:
        stories = get_stories_by_project(db, project_id)
    
    return [
        StoryResponse(
            id=s.id,
            project_id=s.project_id,
            feature_id=s.feature_id,
            title=s.title,
            description=s.description,
            feature_ref=s.feature_ref,
            feature_context=s.feature_context,
            order_index=s.order_index,
            approved=s.approved,
            custom_fields=s.custom_fields or {},
            created_at=s.created_at,
            updated_at=s.updated_at,
            feature_title=s.feature.title if s.feature else None,
        )
        for s in stories
    ]


@router.post("/", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_new_story(
    org_id: str,
    project_id: str,
    story_data: StoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new story."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    # Verify feature exists and belongs to project
    feature = get_feature(db, story_data.feature_id)
    if not feature or feature.project_id != project_id:
        raise HTTPException(status_code=400, detail="Feature not found in this project")
    
    story = create_story(db, project_id, story_data)
    
    return StoryResponse(
        id=story.id,
        project_id=story.project_id,
        feature_id=story.feature_id,
        title=story.title,
        description=story.description,
        feature_ref=story.feature_ref,
        feature_context=story.feature_context,
        order_index=story.order_index,
        approved=story.approved,
        custom_fields=story.custom_fields or {},
        created_at=story.created_at,
        updated_at=story.updated_at,
        feature_title=feature.title,
    )


@router.post("/bulk", response_model=StoryBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_stories_in_bulk(
    org_id: str,
    project_id: str,
    bulk_data: StoryBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple stories at once."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    # Verify all features exist
    for story_data in bulk_data.stories:
        feature = get_feature(db, story_data.feature_id)
        if not feature or feature.project_id != project_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Feature {story_data.feature_id} not found in this project"
            )
    
    stories = create_stories_bulk(db, project_id, bulk_data.stories)
    
    return StoryBulkResponse(
        created=[
            StoryResponse(
                id=s.id,
                project_id=s.project_id,
                feature_id=s.feature_id,
                title=s.title,
                description=s.description,
                feature_ref=s.feature_ref,
                feature_context=s.feature_context,
                order_index=s.order_index,
                approved=s.approved,
                custom_fields=s.custom_fields or {},
                created_at=s.created_at,
                updated_at=s.updated_at,
                feature_title=s.feature.title if s.feature else None,
            )
            for s in stories
        ],
        count=len(stories),
    )


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story_details(
    org_id: str,
    project_id: str,
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get story details."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    story = get_story(db, story_id)
    if not story or story.project_id != project_id:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return StoryResponse(
        id=story.id,
        project_id=story.project_id,
        feature_id=story.feature_id,
        title=story.title,
        description=story.description,
        feature_ref=story.feature_ref,
        feature_context=story.feature_context,
        order_index=story.order_index,
        approved=story.approved,
        custom_fields=story.custom_fields or {},
        created_at=story.created_at,
        updated_at=story.updated_at,
        feature_title=story.feature.title if story.feature else None,
    )


@router.patch("/{story_id}", response_model=StoryResponse)
async def update_story_details(
    org_id: str,
    project_id: str,
    story_id: str,
    story_data: StoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a story."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_story(db, story_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Story not found")
    
    story = update_story(db, story_id, story_data)
    
    return StoryResponse(
        id=story.id,
        project_id=story.project_id,
        feature_id=story.feature_id,
        title=story.title,
        description=story.description,
        feature_ref=story.feature_ref,
        feature_context=story.feature_context,
        order_index=story.order_index,
        approved=story.approved,
        custom_fields=story.custom_fields or {},
        created_at=story.created_at,
        updated_at=story.updated_at,
        feature_title=story.feature.title if story.feature else None,
    )


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story_endpoint(
    org_id: str,
    project_id: str,
    story_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a story."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_story(db, story_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Story not found")
    
    delete_story(db, story_id)


@router.post("/reorder/{feature_id}", response_model=List[StoryResponse])
async def reorder_stories_endpoint(
    org_id: str,
    project_id: str,
    feature_id: str,
    story_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder stories within a feature."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    # Verify feature belongs to project
    feature = get_feature(db, feature_id)
    if not feature or feature.project_id != project_id:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    stories = reorder_stories(db, feature_id, story_ids)
    
    return [
        StoryResponse(
            id=s.id,
            project_id=s.project_id,
            feature_id=s.feature_id,
            title=s.title,
            description=s.description,
            feature_ref=s.feature_ref,
            feature_context=s.feature_context,
            order_index=s.order_index,
            approved=s.approved,
            custom_fields=s.custom_fields or {},
            created_at=s.created_at,
            updated_at=s.updated_at,
            feature_title=s.feature.title if s.feature else None,
        )
        for s in stories
    ]
