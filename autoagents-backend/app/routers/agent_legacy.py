"""Legacy agent endpoints for compatibility with classic frontend."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from ..db import get_database
from ..services.agent1 import Agent1Service
from ..services.agent2 import Agent2Service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["legacy-agent"])
_LEGACY_COLLECTION = "legacy_agent_runs"


class FeatureItem(BaseModel):
    title: str
    description: str = ""
    acceptanceCriteria: list[str] = Field(default_factory=list)


class AgentFeatureRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: str = Field(default="")
    decision: Optional[Literal["again", "keep", "keep_all"]] = None
    run_id: Optional[str] = None
    features: Optional[list[FeatureItem]] = None


class AgentFeatureResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: Optional[str] = None
    features: list[FeatureItem] = Field(default_factory=list)
    stories: list["StoryItem"] = Field(default_factory=list)
    message: str
    decision: Literal["generated", "kept"]
    debug: Optional[dict[str, Any]] = None
    project_id: Optional[str] = None


class StoryItem(BaseModel):
    featureTitle: str
    userStory: str
    acceptanceCriteria: list[str] = Field(default_factory=list)
    implementationNotes: list[str] = Field(default_factory=list)


class AgentStoryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    prompt: str = Field(default="")
    decision: Optional[Literal["again", "keep"]] = None
    run_id: Optional[str] = None
    features: list[FeatureItem] = Field(default_factory=list)
    stories: Optional[list[StoryItem]] = None


class AgentStoryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: Optional[str] = None
    stories: list[StoryItem] = Field(default_factory=list)
    message: str
    decision: Literal["generated", "kept"]


agent2_service = Agent2Service()

@router.post("/features", response_model=AgentFeatureResponse)
async def legacy_generate_features(
    request: AgentFeatureRequest,
    response: Response,
) -> AgentFeatureResponse:
    """Compatibility endpoint for the legacy frontend."""
    logger.debug(f"[legacy-agent] /features endpoint called")
    logger.debug(f"[legacy-agent] Request decision: {request.decision}")
    logger.debug(f"[legacy-agent] Request prompt length: {len(request.prompt) if request.prompt else 0}")
    logger.debug(f"[legacy-agent] Request run_id: {request.run_id}")
    
    # Handle approval flow (keep/keep_all) by echoing features back.
    if request.decision in {"keep", "keep_all"}:
        logger.debug(f"[legacy-agent] Handling keep/keep_all decision")
        if not request.run_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="run_id required when approving features.",
            )
        if not request.features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="features payload required when approving Agent_1 output.",
            )
        await _persist_legacy_run(
            run_id=request.run_id,
            prompt=request.prompt or None,
            features=request.features,
            status="features_kept",
        )
        return AgentFeatureResponse(
            run_id=request.run_id,
            summary=None,
            features=request.features,
            message="Features approved. Proceeding with scope.",
            decision="kept",
            debug=None,
        )

    prompt = (request.prompt or "").strip()
    if not prompt:
        logger.warning(f"[legacy-agent] Empty prompt provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty prompt is required to generate features.",
        )

    logger.info(f"[legacy-agent] Generating features for prompt: {prompt[:100]}...")
    service = Agent1Service()
    try:
        logger.debug(f"[legacy-agent] Starting feature generation for prompt length: {len(prompt)}")
        feature_texts = await service.generate_features(project_title="", project_prompt=prompt)
        logger.info(f"[legacy-agent] Feature generation successful, got {len(feature_texts)} features")
        logger.debug(f"[legacy-agent] Features: {feature_texts[:3] if feature_texts else 'none'}...")
    except RuntimeError as exc:  # Catch Claude runtime errors
        error_detail = str(exc)
        error_type = type(exc).__name__
        
        logger.error(f"[legacy-agent] Agent-1 RuntimeError caught")
        logger.error(f"[legacy-agent] Error type: {error_type}")
        logger.error(f"[legacy-agent] Error detail: {error_detail}")
        logger.debug(f"[legacy-agent] Full exception traceback:", exc_info=True)
        
        # Check for specific error types to provide better HTTP status codes
        error_detail_lower = error_detail.lower()
        
        # Credit balance errors should be 402 Payment Required or 503 Service Unavailable
        if "credit balance" in error_detail_lower or "too low" in error_detail_lower:
            logger.error(f"[legacy-agent] Credit balance error detected, returning 402 Payment Required")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=error_detail,  # User-friendly message from agent1
            ) from exc
        
        # Authentication errors should be 401 Unauthorized
        if "authentication" in error_detail_lower or "api key" in error_detail_lower:
            logger.error(f"[legacy-agent] Authentication error detected, returning 401 Unauthorized")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_detail,
            ) from exc
        
        # Rate limit errors should be 429 Too Many Requests
        if "rate limit" in error_detail_lower:
            logger.error(f"[legacy-agent] Rate limit error detected, returning 429 Too Many Requests")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_detail,
            ) from exc
        
        # Generic service unavailable for other errors
        logger.error(f"[legacy-agent] Generic service error, returning 503 Service Unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_detail,
        ) from exc
    except Exception as exc:  # Catch any other unexpected errors
        error_detail = str(exc)
        error_type = type(exc).__name__
        
        logger.error(f"[legacy-agent] Agent-1 unexpected error caught")
        logger.error(f"[legacy-agent] Error type: {error_type}")
        logger.error(f"[legacy-agent] Error detail: {error_detail}")
        logger.debug(f"[legacy-agent] Full exception traceback:", exc_info=True)
        
        # Include error type and details in response for debugging
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent-1 failed ({error_type}): {error_detail}",
        ) from exc

    features = [FeatureItem(title=text.strip()) for text in feature_texts]
    run_id = request.run_id or str(uuid.uuid4())
    await _persist_legacy_run(
        run_id=run_id,
        prompt=prompt,
        features=features,
        status="features_generated",
    )

    return AgentFeatureResponse(
        run_id=run_id,
        summary=None,
        features=features,
        message="Generated feature concepts.",
        decision="generated",
        debug=None,
    )


@router.post("/stories", response_model=AgentStoryResponse)
async def legacy_generate_stories(request: AgentStoryRequest) -> AgentStoryResponse:
    """Compatibility endpoint for generating user stories via legacy UI."""
    run_id = request.run_id or str(uuid.uuid4())

    if request.decision == "keep":
        if not request.run_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="run_id required when approving stories.",
            )
        stories_payload = request.stories or []
        if not stories_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="stories payload required when approving Agent_2 output.",
            )
        await _persist_legacy_run(
            run_id=request.run_id,
            stories=stories_payload,
            status="stories_kept",
        )
        return AgentStoryResponse(
            run_id=request.run_id,
            summary=None,
            stories=stories_payload,
            message="Stories approved and saved.",
            decision="kept",
        )

    features = request.features
    if not features:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one feature is required to generate stories.",
        )

    prompt = (request.prompt or "").strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty prompt is required to generate stories.",
        )

    feature_documents: list[dict[str, Any]] = []
    for idx, feature in enumerate(features, start=1):
        feature_documents.append(
            {
                "_id": f"legacy-feature-{idx}",
                "feature_text": feature.title or feature.description or "Feature",
            }
        )

    try:
        # Pass original prompt to agent2 for context-aware story generation
        generated = await agent2_service.generate_stories(feature_documents, original_prompt=prompt)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    stories = [
        StoryItem(
            featureTitle=story.get("feature_text", "Feature"),
            userStory=story.get("story_text", "As a user, I want ..."),
            acceptanceCriteria=story.get("acceptance_criteria", []),
        )
        for story in generated
    ]

    await _persist_legacy_run(
        run_id=run_id,
        prompt=prompt,
        features=features,
        stories=stories,
        status="stories_generated",
    )

    return AgentStoryResponse(
        run_id=run_id,
        summary=None,
        stories=stories,
        message="Generated user stories.",
        decision="generated",
    )


async def _persist_legacy_run(
    run_id: str,
    *,
    prompt: str | None = None,
    features: list[FeatureItem] | None = None,
    stories: list[StoryItem] | None = None,
    status: str | None = None,
) -> None:
    """Persist the legacy agent run so MongoDB keeps a history."""
    db = get_database()
    now = datetime.utcnow()
    update_fields: dict[str, Any] = {"updated_at": now}

    if prompt is not None:
        update_fields["prompt"] = prompt
    if features is not None:
        update_fields["features"] = [feature.model_dump() for feature in features]
    if stories is not None:
        update_fields["stories"] = [story.model_dump() for story in stories]
    if status is not None:
        update_fields["status"] = status

    await db[_LEGACY_COLLECTION].update_one(
        {"run_id": run_id},
        {
            "$set": update_fields,
            "$setOnInsert": {"run_id": run_id, "created_at": now},
        },
        upsert=True,
    )
