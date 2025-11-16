"""Feature endpoints for AutoAgents backend."""

from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from ..db import get_database
from ..schemas.feature import FeatureModel
from ..services.agent1 import generate_features_for_project

router = APIRouter(prefix="/projects/{project_id}/features", tags=["features"])


@router.post("/generate", response_model=List[FeatureModel])
async def generate_features(project_id: str) -> List[FeatureModel]:
    """Generate features for a project via OpenAI and persist them."""
    db = get_database()
    features = await generate_features_for_project(project_id, db)
    return [
        FeatureModel.model_validate(
            {
                "id": feature["_id"],
                "project_id": feature["project_id"],
                "feature_text": feature["feature_text"],
                "order_index": feature["order_index"],
                "created_at": feature["created_at"],
            }
        )
        for feature in features
    ]


@router.get("", response_model=List[FeatureModel])
async def list_features(project_id: str) -> List[FeatureModel]:
    """List features associated with a project."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    db = get_database()
    cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    records = await cursor.to_list(length=None)

    return [
        FeatureModel.model_validate(
            {
                "id": str(record["_id"]),
                "project_id": record["project_id"],
                "feature_text": record["feature_text"],
                "order_index": record["order_index"],
                "created_at": record["created_at"],
            }
        )
        for record in records
    ]

