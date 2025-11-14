"""Legacy agent endpoints for compatibility with classic frontend."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field

from ..db import get_database
from ..services.agent1 import Agent1Service
from ..services.agent2 import Agent2Service

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
    # Handle approval flow (keep/keep_all) by echoing features back.
    if request.decision in {"keep", "keep_all"}:
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty prompt is required to generate features.",
        )

    service = Agent1Service()
    try:
        feature_texts = await service.generate_features(project_title="", project_prompt=prompt)
    except RuntimeError as exc:  # Catch Claude runtime errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
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
        generated = await agent2_service.generate_stories(feature_documents)
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
