"""Diagram endpoints for AutoAgents backend."""

from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from ..db import get_database
from ..schemas.diagram import DiagramModel
from ..services import Agent3Service

router = APIRouter(prefix="/projects/{project_id}/diagram", tags=["diagram"])
agent3_service = Agent3Service()


@router.post("/generate", response_model=DiagramModel)
async def generate_diagram(project_id: str) -> DiagramModel:
    """Generate a Mermaid diagram for a project via Agent-3."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    features = await db["features"].find({"project_id": project_id}).to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No features available for diagram generation.",
        )

    stories = await db["stories"].find({"project_id": project_id}).to_list(length=None)
    if not stories:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No stories available for diagram generation.",
        )

    try:
        mermaid_source = await agent3_service.generate_mermaid(
            project_title=project.get("title", ""),
            features=features,
            stories=stories,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc

    await db["diagrams"].delete_many({"project_id": project_id})

    document = {
        "project_id": project_id,
        "diagram_type": "mermaid",
        "mermaid_source": mermaid_source,
        "created_at": datetime.utcnow(),
    }

    result = await db["diagrams"].insert_one(document)
    document["_id"] = result.inserted_id
    document["id"] = str(result.inserted_id)

    return DiagramModel.model_validate(document)


@router.get("", response_model=DiagramModel)
async def get_diagram(project_id: str) -> DiagramModel:
    """Retrieve the latest generated diagram for a project."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    document = await db["diagrams"].find_one(
        {"project_id": project_id},
        sort=[("created_at", -1)],
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found.")

    document["id"] = str(document["_id"])
    return DiagramModel.model_validate(document)

