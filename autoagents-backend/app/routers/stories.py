"""Story endpoints for AutoAgents backend."""

from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from ..db import get_database
from ..schemas.story import StoryModel
from ..services import Agent2Service

router = APIRouter(prefix="/projects/{project_id}/stories", tags=["stories"])
agent2_service = Agent2Service()


@router.post("/generate", response_model=List[StoryModel])
async def generate_stories(project_id: str) -> List[StoryModel]:
    """Generate stories for a project's features via Agent-2."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    features = await db["features"].find({"project_id": project_id}).to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No features available for story generation.",
        )

    try:
        generated_stories = await agent2_service.generate_stories(features)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    await db["stories"].delete_many({"project_id": project_id})

    now = datetime.utcnow()
    documents = []
    for story in generated_stories:
        documents.append(
            {
                "project_id": project_id,
                "feature_id": story.get("feature_id"),
                "story_text": story.get("story_text", ""),
                "acceptance_criteria": story.get("acceptance_criteria", []),
                "created_at": now,
            }
        )

    if not documents:
        return []

    result = await db["stories"].insert_many(documents)
    for document, inserted_id in zip(documents, result.inserted_ids):
        document["_id"] = inserted_id
        document["id"] = str(inserted_id)

    return [StoryModel.model_validate(document) for document in documents]


@router.get("", response_model=List[StoryModel])
async def list_stories(project_id: str) -> List[StoryModel]:
    """List stories associated with a project."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    records = await cursor.to_list(length=None)

    return [
        StoryModel.model_validate({**record, "id": str(record["_id"])})
        for record in records
    ]

