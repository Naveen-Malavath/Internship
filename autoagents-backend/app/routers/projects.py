"""Project router for AutoAgents backend."""

from datetime import datetime
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from ..db import get_database
from ..services.agent2 import generate_stories_for_project
from ..services.agent3 import generate_diagram_for_project, generate_designs_for_project
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


@router.post("/{project_id}/stories/generate")
async def generate_project_stories(project_id: str) -> List[Dict[str, Any]]:
    """Trigger Agent-2 to generate stories for a given project."""
    db = get_database()
    stories = await generate_stories_for_project(project_id, db)
    return stories


@router.get("/{project_id}/stories")
async def list_project_stories(project_id: str) -> List[Dict[str, Any]]:
    """Return all stories for a project, ordered by creation time."""
    db = get_database()
    cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    records = await cursor.to_list(length=None)

    stories: List[Dict[str, Any]] = []
    for record in records:
        story = dict(record)
        story["_id"] = str(story["_id"])
        if "feature_id" in story and story["feature_id"] is not None:
            story["feature_id"] = str(story["feature_id"])
        stories.append(story)

    return stories


@router.post("/{project_id}/diagram/generate")
async def generate_project_diagram(project_id: str) -> Dict[str, Any]:
    """Trigger Agent-3 to generate a system diagram for a project."""
    db = get_database()
    diagram = await generate_diagram_for_project(project_id, db)
    return diagram


@router.get("/{project_id}/diagram")
async def get_latest_project_diagram(project_id: str) -> Dict[str, Any]:
    """Return the most recent diagram for the project."""
    db = get_database()
    cursor = (
        db["diagrams"]
        .find({"project_id": project_id})
        .sort("created_at", -1)
        .limit(1)
    )
    records = await cursor.to_list(length=1)
    if not records:
        raise HTTPException(status_code=404, detail="No diagram found for this project")

    diagram = dict(records[0])
    diagram["_id"] = str(diagram["_id"])
    return diagram


@router.post("/{project_id}/designs/generate")
async def generate_project_designs(project_id: str) -> Dict[str, Any]:
    """Trigger Agent-3 to generate HLD, LLD, and DBD designs for a project."""
    db = get_database()
    designs = await generate_designs_for_project(project_id, db)
    return designs


@router.get("/{project_id}/designs")
async def get_latest_project_designs(project_id: str) -> Dict[str, Any]:
    """Return the most recent designs for the project."""
    db = get_database()
    cursor = (
        db["designs"]
        .find({"project_id": project_id})
        .sort("created_at", -1)
        .limit(1)
    )
    records = await cursor.to_list(length=1)
    if not records:
        raise HTTPException(
            status_code=404, detail="No designs found for this project. Run Agent-3 first."
        )

    design = dict(records[0])
    design["_id"] = str(design["_id"])
    return design

