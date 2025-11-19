from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["status"])


@router.get("/right-now", summary="Current status snapshot")
async def status_right_now() -> dict[str, str]:
    """Return a lightweight status message for the frontend."""
    return {"status": "All systems operational."}



