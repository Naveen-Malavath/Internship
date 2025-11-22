"""Visualizer endpoints for legacy compatibility with classic frontend."""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

from ..agents import ClaudeVisualizationAgent, FeatureSpec, StorySpec
from ..services.claude_client import DEFAULT_CLAUDE_MODEL
from ..services import Agent3Service
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
    # Priority: CLAUDE_MODEL_DEBUG > CLAUDE_MODEL > DEFAULT_CLAUDE_MODEL
    model = os.getenv("CLAUDE_MODEL_DEBUG") or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
    return ClaudeVisualizationAgent(api_key=api_key, model=model)


@router.post("", response_model=AgentVisualizationResponse)
async def agent_visualizer(request: AgentVisualizationRequest) -> AgentVisualizationResponse:
    """Generate visualization artifacts with Agent_3 for legacy compatibility."""
    import uuid
    
    # Determine diagram type (default to 'hld' if not provided)
    diagram_type = (request.diagramType or "hld").lower()
    valid_types = {"hld", "lld", "database"}
    if diagram_type not in valid_types:
        diagram_type = "hld"
    
    feature_items = request.features or []
    story_items = request.stories or []

    # Convert to feature/story dicts for Agent3Service
    feature_dicts = [
        {
            "title": item.title,
            "feature_text": item.title,
            "description": item.description,
        }
        for item in feature_items
    ]
    if not feature_dicts:
        # Load from snapshot and convert
        feature_specs = load_agent1_features()
        feature_dicts = [
            {
                "title": feat.title,
                "feature_text": feat.title,
                "description": feat.description,
            }
            for feat in feature_specs
        ]

    story_dicts = [
        {
            "feature_id": item.featureTitle,
            "story_text": item.userStory,
            "user_story": item.userStory,
            "acceptance_criteria": item.acceptanceCriteria,
            "implementation_notes": item.implementationNotes,
        }
        for item in story_items
    ]
    if not story_dicts:
        # Load from snapshot and convert
        story_specs = load_agent2_stories()
        story_dicts = [
            {
                "feature_id": story.feature_title,
                "story_text": story.user_story,
                "user_story": story.user_story,
                "acceptance_criteria": story.acceptance_criteria,
                "implementation_notes": story.implementation_notes,
            }
            for story in story_specs
        ]

    if not feature_dicts or not story_dicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visualization requires approved features and stories.",
        )

    # Get prompt from storage or use empty string
    original_prompt = request.prompt or load_prompt() or ""
    project_title = "Project"  # Default title for legacy endpoint

    # Use Agent3Service for diagram type-aware generation
    # Check API key before initializing service
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("[visualizer] Claude API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent_3 is unavailable. Missing Claude API configuration. Please set CLAUDE_API_KEY or ANTHROPIC_API_KEY environment variable.",
        )
    
    try:
        logger.info(f"[visualizer] Generating {diagram_type.upper()} diagram | features={len(feature_dicts)} | stories={len(story_dicts)}")
        agent3_service = Agent3Service()
        mermaid_diagram = await agent3_service.generate_mermaid(
            project_title=project_title,
            features=feature_dicts,
            stories=story_dicts,
            diagram_type=diagram_type,
            original_prompt=original_prompt,
        )
        
        # Generate a simple DOT diagram as fallback (Agent3Service doesn't return DOT)
        dot_diagram = f"digraph G {{\n  // {diagram_type.upper()} diagram\n  label=\"{project_title}\";\n}}"
        
        run_id = str(uuid.uuid4())
        logger.info(f"[visualizer] Successfully generated {diagram_type.upper()} diagram | mermaid_length={len(mermaid_diagram)}")
        
    except RuntimeError as exc:
        # RuntimeError usually means API key or client initialization issue
        logger.error(f"[visualizer] RuntimeError generating visualization: {exc}", exc_info=True)
        error_msg = str(exc)
        if "API key" in error_msg or "not configured" in error_msg:
            detail = "Agent_3 is unavailable. Missing or invalid Claude API configuration."
        else:
            detail = f"Failed to initialize Agent_3: {error_msg}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        ) from exc
    except Exception as exc:
        # Catch any other exceptions (API errors, network issues, etc.)
        logger.error(f"[visualizer] Exception generating visualization: {type(exc).__name__}: {exc}", exc_info=True)
        error_msg = str(exc)
        # Provide more specific error messages
        if "API key" in error_msg or "authentication" in error_msg.lower():
            detail = "Authentication failed. Please check your Claude API key."
        elif "rate limit" in error_msg.lower() or "429" in error_msg:
            detail = "Rate limit exceeded. Please try again in a moment."
        elif "timeout" in error_msg.lower() or "network" in error_msg.lower():
            detail = "Network error. Please check your connection and try again."
        else:
            detail = f"Failed to generate visualization: {error_msg}"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        ) from exc

    # Store the newly generated visualization
    store_visualization_assets(mermaid_diagram, dot_diagram)
    mermaid_text, mermaid_path, mermaid_updated_at = load_mermaid_asset()
    dot_text, dot_path, dot_updated_at = load_dot_asset()

    diagrams = VisualizationDiagram(
        mermaid=mermaid_text or mermaid_diagram,
        dot=dot_text or dot_diagram,
        mermaidPath=mermaid_path,
        dotPath=dot_path,
        mermaidUpdatedAt=mermaid_updated_at,
        dotUpdatedAt=dot_updated_at,
    )

    return AgentVisualizationResponse(
        run_id=run_id,
        summary=f"Generated {diagram_type.upper()} diagram using Agent-3.",
        diagrams=diagrams,
        callouts=[],
        message=f"Generated {diagram_type.upper()} visualization blueprint.",
        debug={"diagram_type": diagram_type},
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

