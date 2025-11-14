from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ..db import get_database


router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", summary="Create a new project")
async def create_project(payload: dict[str, str]) -> dict[str, object]:
    user_id = payload.get("user_id")
    title = payload.get("title")
    prompt = payload.get("prompt")

    if not user_id or not title or not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fields 'user_id', 'title', and 'prompt' are required.",
        )

    db = get_database()
    created_at = datetime.now(timezone.utc)
    document = {
        "user_id": user_id,
        "title": title,
        "prompt": prompt,
        "status": "created",
        "created_at": created_at,
    }

    result = await db["projects"].insert_one(document)
    document["_id"] = str(result.inserted_id)
    document["created_at"] = created_at.isoformat()
    return document

