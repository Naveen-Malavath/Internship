from __future__ import annotations

from fastapi import APIRouter

from ..db import get_database

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/ping-db", summary="Check MongoDB connectivity")
async def ping_db() -> dict[str, object]:
    db = get_database()
    collections = await db.list_collection_names()
    return {"status": "ok", "collections": collections}

