"""Diagram endpoints for AutoAgents backend."""

from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel

from ..db import get_database
from ..schemas.diagram import DiagramModel
from ..services import Agent3Service

router = APIRouter(prefix="/projects/{project_id}/diagram", tags=["diagram"])
agent3_service = Agent3Service()


class DiagramGenerateRequest(BaseModel):
    diagram_type: str = "hld"  # Options: "hld", "lld", "database"


@router.post("/generate", response_model=DiagramModel)
async def generate_diagram(
    project_id: str,
    request: DiagramGenerateRequest = Body(default_factory=lambda: DiagramGenerateRequest()),
) -> DiagramModel:
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

    # Validate diagram type
    valid_types = {"hld", "lld", "database"}
    diagram_type = request.diagram_type.lower()
    if diagram_type not in valid_types:
        diagram_type = "hld"  # Default to HLD if invalid

    try:
        mermaid_source = await agent3_service.generate_mermaid(
            project_title=project.get("title", ""),
            features=features,
            stories=stories,
            diagram_type=diagram_type,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        ) from exc
    except Exception as exc:
        # Catch any other exceptions to prevent 500 errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate diagram: {str(exc)}",
        ) from exc

    await db["diagrams"].delete_many({"project_id": project_id, "diagram_type": diagram_type})

    document = {
        "project_id": project_id,
        "diagram_type": diagram_type,
        "mermaid_source": mermaid_source,
        "created_at": datetime.utcnow(),
    }

    result = await db["diagrams"].insert_one(document)
    document["_id"] = result.inserted_id
    document["id"] = str(result.inserted_id)

    return DiagramModel.model_validate(document)


@router.get("", response_model=DiagramModel)
async def get_diagram(project_id: str, diagram_type: str = "hld") -> DiagramModel:
    """Retrieve the latest generated diagram for a project."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    # Validate and normalize diagram type
    valid_types = {"hld", "lld", "database"}
    normalized_type = diagram_type.lower()
    if normalized_type not in valid_types:
        normalized_type = "hld"

    document = await db["diagrams"].find_one(
        {"project_id": project_id, "diagram_type": normalized_type},
        sort=[("created_at", -1)],
    )
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagram not found.")

    document["id"] = str(document["_id"])
    return DiagramModel.model_validate(document)

