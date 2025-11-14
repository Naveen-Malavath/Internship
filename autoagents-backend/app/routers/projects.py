"""Project router for AutoAgents backend."""

from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from ..db import get_database
from ..schemas.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects() -> List[ProjectResponse]:
    """Return all projects sorted by creation time (newest first)."""
    db = get_database()
    cursor = db["projects"].find().sort("created_at", -1)
    records = await cursor.to_list(length=None)

    return [
        ProjectResponse.model_validate(
            {
                "id": str(record["_id"]),
                "user_id": record["user_id"],
                "title": record["title"],
                "prompt": record["prompt"],
                "status": record.get("status", "created"),
                "created_at": record["created_at"],
            }
        )
        for record in records
    ]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> ProjectResponse:
    """Create a new project document."""
    db = get_database()
    document = payload.model_dump()
    document["status"] = "created"
    document["created_at"] = datetime.utcnow()

    result = await db["projects"].insert_one(document)
    document["_id"] = str(result.inserted_id)
    document["id"] = document["_id"]
    document["created_at"] = document["created_at"]
    return ProjectResponse.model_validate(document)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str) -> ProjectResponse:
    """Fetch a single project by its identifier."""
    db = get_database()
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    document = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    document["id"] = str(document["_id"])
    return ProjectResponse.model_validate(document)


@router.get("/user/{user_id}")
async def get_projects_by_user_placeholder(user_id: str) -> dict[str, str]:
    """Placeholder for fetching projects by user."""
    return {"message": f"Get projects for user {user_id} placeholder"}

