"""Visualizer endpoints for legacy compatibility with classic frontend."""

from __future__ import annotations

import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from ..agents import ClaudeVisualizationAgent, FeatureSpec, StorySpec
from ..services.claude_client import DEFAULT_CLAUDE_MODEL
from ..storage import load_agent1_features, load_agent2_stories, load_prompt, load_mermaid_asset, load_dot_asset, store_visualization_assets

router = APIRouter(prefix="/agent/visualizer", tags=["legacy-visualizer"])


class FeatureItem(BaseModel):
    title: str
    description: str = ""
    acceptanceCriteria: list[str] = Field(default_factory=list)


class StoryItem(BaseModel):
    featureTitle: str
    userStory: str
    acceptanceCriteria: list[str] = Field(default_factory=list)
    implementationNotes: list[str] = Field(default_factory=list)


class VisualizationDiagram(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    mermaid: str
    dot: str
    mermaidPath: Optional[str] = Field(default=None)
    dotPath: Optional[str] = Field(default=None)
    mermaidUpdatedAt: Optional[str] = Field(default=None)
    dotUpdatedAt: Optional[str] = Field(default=None)


class AgentVisualizationRequest(BaseModel):
    prompt: Optional[str] = None
    features: Optional[list[FeatureItem]] = None
    stories: Optional[list[StoryItem]] = None
    diagramType: Optional[str] = None  # Not used in legacy endpoint, but accepted for compatibility


class AgentVisualizationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    run_id: str
    summary: str
    diagrams: VisualizationDiagram
    callouts: list[str] = Field(default_factory=list)
    message: str
    debug: Optional[dict[str, Any]] = None


class MermaidAssetResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, ser_json_by_alias=True)

    mermaid: str
    path: Optional[str] = None
    updatedAt: Optional[str] = Field(default=None)


class MermaidAssetUpdateRequest(BaseModel):
    mermaid: str


def _get_agent3() -> ClaudeVisualizationAgent:
    """Get initialized Agent3 instance."""
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent_3 is unavailable. Missing Claude API configuration.",
        )
    return ClaudeVisualizationAgent(api_key=api_key, model=os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL))


@router.post("", response_model=AgentVisualizationResponse)
async def agent_visualizer(request: AgentVisualizationRequest) -> AgentVisualizationResponse:
    """Generate visualization artifacts with Agent_3 for legacy compatibility."""
    agent_3 = _get_agent3()

    feature_items = request.features or []
    story_items = request.stories or []

    feature_specs = [
        FeatureSpec(
            title=item.title,
            description=item.description,
            acceptance_criteria=item.acceptanceCriteria,
        )
        for item in feature_items
    ]
    if not feature_specs:
        feature_specs = load_agent1_features()

    story_specs = [
        StorySpec(
            feature_title=item.featureTitle,
            user_story=item.userStory,
            acceptance_criteria=item.acceptanceCriteria,
            implementation_notes=item.implementationNotes,
        )
        for item in story_items
    ]
    if not story_specs:
        story_specs = load_agent2_stories()

    if not feature_specs or not story_specs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visualization requires approved features and stories.",
        )

    try:
        visualization = await agent_3.generate_visualization(feature_specs, story_specs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to generate visualization: {exc}",
        ) from exc

    store_visualization_assets(visualization.mermaid, visualization.dot)
    mermaid_text, mermaid_path, mermaid_updated_at = load_mermaid_asset()
    dot_text, dot_path, dot_updated_at = load_dot_asset()

    diagrams = VisualizationDiagram(
        mermaid=mermaid_text or visualization.mermaid,
        dot=dot_text or visualization.dot,
        mermaidPath=mermaid_path,
        dotPath=dot_path,
        mermaidUpdatedAt=mermaid_updated_at,
        dotUpdatedAt=dot_updated_at,
    )

    return AgentVisualizationResponse(
        run_id=visualization.run_id,
        summary=visualization.summary,
        diagrams=diagrams,
        callouts=visualization.callouts,
        message="Generated visualization blueprint.",
        debug=visualization.debug,
    )


@router.get("/mermaid", response_model=MermaidAssetResponse)
async def get_mermaid_asset() -> MermaidAssetResponse:
    """Retrieve the latest Mermaid diagram asset."""
    mermaid, path, updated_at = load_mermaid_asset()
    return MermaidAssetResponse(mermaid=mermaid, path=path, updatedAt=updated_at)


@router.post("/mermaid", response_model=MermaidAssetResponse)
async def save_mermaid_asset(payload: MermaidAssetUpdateRequest) -> MermaidAssetResponse:
    """Persist Mermaid diagram edits."""
    mermaid = payload.mermaid.strip()
    if not mermaid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mermaid diagram cannot be empty.",
        )

    store_visualization_assets(mermaid, None)
    saved_mermaid, path, updated_at = load_mermaid_asset()
    return MermaidAssetResponse(mermaid=saved_mermaid, path=path, updatedAt=updated_at)

