"""
Feature management router.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, OrgRole
from routers.auth import get_current_user
from routers.organizations import require_org_member
from routers.projects import require_project_access
from schemas.feature import (
    FeatureCreate, FeatureUpdate, FeatureResponse,
    FeatureBulkCreate, FeatureBulkResponse
)
from crud.feature import (
    get_feature, get_feature_with_story_count, get_features_by_project,
    create_feature, create_features_bulk, update_feature, delete_feature,
    reorder_features
)
from crud.story import get_story_count_by_feature

router = APIRouter(
    prefix="/api/organizations/{org_id}/projects/{project_id}/features",
    tags=["Features"]
)


@router.get("/", response_model=List[FeatureResponse])
async def list_features(
    org_id: str,
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all features for a project."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    features = get_features_by_project(db, project_id)
    
    return [
        FeatureResponse(
            id=f.id,
            project_id=f.project_id,
            title=f.title,
            reason=f.reason,
            problem_statement=f.problem_statement,
            business_objective=f.business_objective,
            user_persona=f.user_persona,
            acceptance_criteria=f.acceptance_criteria,
            detailed_description=f.detailed_description,
            success_metrics=f.success_metrics,
            dependencies=f.dependencies,
            order_index=f.order_index,
            approved=f.approved,
            custom_fields=f.custom_fields or {},
            created_at=f.created_at,
            updated_at=f.updated_at,
            story_count=get_story_count_by_feature(db, f.id),
        )
        for f in features
    ]


@router.post("/", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
async def create_new_feature(
    org_id: str,
    project_id: str,
    feature_data: FeatureCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new feature."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    feature = create_feature(db, project_id, feature_data)
    
    return FeatureResponse(
        id=feature.id,
        project_id=feature.project_id,
        title=feature.title,
        reason=feature.reason,
        problem_statement=feature.problem_statement,
        business_objective=feature.business_objective,
        user_persona=feature.user_persona,
        acceptance_criteria=feature.acceptance_criteria,
        detailed_description=feature.detailed_description,
        success_metrics=feature.success_metrics,
        dependencies=feature.dependencies,
        order_index=feature.order_index,
        approved=feature.approved,
        custom_fields=feature.custom_fields or {},
        created_at=feature.created_at,
        updated_at=feature.updated_at,
        story_count=0,
    )


@router.post("/bulk", response_model=FeatureBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_features_in_bulk(
    org_id: str,
    project_id: str,
    bulk_data: FeatureBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple features at once."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    features = create_features_bulk(db, project_id, bulk_data.features)
    
    return FeatureBulkResponse(
        created=[
            FeatureResponse(
                id=f.id,
                project_id=f.project_id,
                title=f.title,
                reason=f.reason,
                problem_statement=f.problem_statement,
                business_objective=f.business_objective,
                user_persona=f.user_persona,
                acceptance_criteria=f.acceptance_criteria,
                detailed_description=f.detailed_description,
                success_metrics=f.success_metrics,
                dependencies=f.dependencies,
                order_index=f.order_index,
                approved=f.approved,
                custom_fields=f.custom_fields or {},
                created_at=f.created_at,
                updated_at=f.updated_at,
                story_count=0,
            )
            for f in features
        ],
        count=len(features),
    )


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature_details(
    org_id: str,
    project_id: str,
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get feature details."""
    require_project_access(db, org_id, project_id, current_user.id)
    
    result = get_feature_with_story_count(db, feature_id)
    if not result or result["feature"].project_id != project_id:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    feature = result["feature"]
    
    return FeatureResponse(
        id=feature.id,
        project_id=feature.project_id,
        title=feature.title,
        reason=feature.reason,
        problem_statement=feature.problem_statement,
        business_objective=feature.business_objective,
        user_persona=feature.user_persona,
        acceptance_criteria=feature.acceptance_criteria,
        detailed_description=feature.detailed_description,
        success_metrics=feature.success_metrics,
        dependencies=feature.dependencies,
        order_index=feature.order_index,
        approved=feature.approved,
        custom_fields=feature.custom_fields or {},
        created_at=feature.created_at,
        updated_at=feature.updated_at,
        story_count=result["story_count"],
    )


@router.patch("/{feature_id}", response_model=FeatureResponse)
async def update_feature_details(
    org_id: str,
    project_id: str,
    feature_id: str,
    feature_data: FeatureUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a feature."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    # Verify feature belongs to project
    existing = get_feature(db, feature_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    feature = update_feature(db, feature_id, feature_data)
    
    return FeatureResponse(
        id=feature.id,
        project_id=feature.project_id,
        title=feature.title,
        reason=feature.reason,
        problem_statement=feature.problem_statement,
        business_objective=feature.business_objective,
        user_persona=feature.user_persona,
        acceptance_criteria=feature.acceptance_criteria,
        detailed_description=feature.detailed_description,
        success_metrics=feature.success_metrics,
        dependencies=feature.dependencies,
        order_index=feature.order_index,
        approved=feature.approved,
        custom_fields=feature.custom_fields or {},
        created_at=feature.created_at,
        updated_at=feature.updated_at,
        story_count=get_story_count_by_feature(db, feature.id),
    )


@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature_endpoint(
    org_id: str,
    project_id: str,
    feature_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a feature and its stories."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    existing = get_feature(db, feature_id)
    if not existing or existing.project_id != project_id:
        raise HTTPException(status_code=404, detail="Feature not found")
    
    delete_feature(db, feature_id)


@router.post("/reorder", response_model=List[FeatureResponse])
async def reorder_features_endpoint(
    org_id: str,
    project_id: str,
    feature_ids: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reorder features by providing new order of IDs."""
    require_project_access(db, org_id, project_id, current_user.id, require_write=True)
    
    features = reorder_features(db, project_id, feature_ids)
    
    return [
        FeatureResponse(
            id=f.id,
            project_id=f.project_id,
            title=f.title,
            reason=f.reason,
            problem_statement=f.problem_statement,
            business_objective=f.business_objective,
            user_persona=f.user_persona,
            acceptance_criteria=f.acceptance_criteria,
            detailed_description=f.detailed_description,
            success_metrics=f.success_metrics,
            dependencies=f.dependencies,
            order_index=f.order_index,
            approved=f.approved,
            custom_fields=f.custom_fields or {},
            created_at=f.created_at,
            updated_at=f.updated_at,
            story_count=get_story_count_by_feature(db, f.id),
        )
        for f in features
    ]
