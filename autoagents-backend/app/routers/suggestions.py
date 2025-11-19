"""AI suggestion endpoints for project wizard."""

from __future__ import annotations

import os
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from ..agents import ClaudeSuggestionAgent

router = APIRouter(prefix="/agent/suggestions", tags=["ai-suggestions"])


class SuggestionRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    suggestion_type: Literal["summary", "epics", "acceptanceCriteria", "stories"] = Field(
        description="Type of suggestion to generate"
    )
    prompt: str = Field(description="The prompt template to use")
    project_context: Optional[dict[str, Any]] = Field(
        default=None, description="Optional project details for context"
    )


class SuggestionResponse(BaseModel):
    run_id: str
    output: str
    type: str


@router.post("", response_model=SuggestionResponse)
async def generate_suggestion(request: SuggestionRequest) -> SuggestionResponse:
    """Generate AI suggestions for project wizard (summary, epics, acceptance criteria, risks)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ANTHROPIC_API_KEY not configured",
        )

    agent = ClaudeSuggestionAgent(api_key=api_key)

    try:
        result = await agent.generate_suggestion(
            suggestion_type=request.suggestion_type,
            prompt=request.prompt,
            project_context=request.project_context,
        )
        return SuggestionResponse(
            run_id=result["run_id"],
            output=result["output"],
            type=result["type"],
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI suggestion generation failed: {str(exc)}",
        ) from exc

