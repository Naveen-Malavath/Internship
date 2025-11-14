"""Auth router placeholder."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/placeholder")
async def auth_placeholder() -> dict[str, str]:
    """Placeholder endpoint."""
    return {"message": "Auth router placeholder"}

