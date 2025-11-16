"""Agent-3 service responsible for Mermaid diagram generation."""

from __future__ import annotations

import datetime
import os
from typing import Any, Dict, List

import anthropic
from anthropic import APIError
from bson import ObjectId
from fastapi import HTTPException

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    extract_text,
    get_claude_client,
)


class Agent3Service:
    """Service wrapper for generating Mermaid diagrams via Claude."""

    def __init__(self, model: str = DEFAULT_CLAUDE_MODEL) -> None:
        self.model = model

    async def generate_mermaid(self, project_title: str, features: List[Dict], stories: List[Dict]) -> str:
        """Generate a Mermaid diagram linking project features and stories."""
        client = get_claude_client()

        feature_outline = "\n".join(
            f"- {feature.get('feature_text')}" for feature in features
        )
        story_outline = "\n".join(
            f"- Feature ID {story.get('feature_id')}: {story.get('story_text')}"
            for story in stories
        )

        user_prompt = (
            "You are Agent-3, an AI architect. Produce a Mermaid flowchart using graph TD syntax. "
            "The diagram must include the project as the start node, features as intermediate nodes, "
            "and user stories as downstream nodes. Output ONLY the Mermaid source, no explanation.\n\n"
            f"Project: {project_title or 'Untitled Project'}\n"
            f"Features:\n{feature_outline or 'None'}\n\n"
            f"Stories:\n{story_outline or 'None'}"
        )

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=800,
                temperature=0.35,
                system="Return only valid Mermaid flowchart code.",
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
        except APIError as exc:
            raise RuntimeError(f"Agent-3 failed to generate diagram: {exc}") from exc

        mermaid = extract_text(response).strip()
        if not mermaid.startswith("graph"):
            mermaid = f"graph TD\n{mermaid}"
        return mermaid


async def generate_diagram_for_project(project_id: str, db) -> Dict[str, Any]:
    """Generate and persist a Mermaid system diagram for a given project."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid project ID") from exc

    project = await db["projects"].find_one({"_id": object_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=400, detail="No features found for this project. Run Agent-1 first."
        )

    stories_cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    stories = await stories_cursor.to_list(length=None)

    project_title = project.get("title") or "Untitled Project"
    project_description = project.get("prompt") or project.get("description") or ""

    feature_lines = "\n".join(
        f"{idx}. {feature.get('feature_text') or feature.get('title') or 'Feature'}"
        for idx, feature in enumerate(features, start=1)
    )
    story_lines = "\n".join(
        f"{idx}. {story.get('story_text') or 'As a user, I want ...'}"
        for idx, story in enumerate(stories, start=1)
    )

    prompt_sections = [
        "You are a senior software architect.",
        f"Project title: {project_title}",
        f"Project description: {project_description}",
        "",
        "Main features:",
        feature_lines or "None provided",
        "",
        "Example user stories:",
        story_lines or "None provided",
        "",
        "Task:",
        "Design a high-level system architecture / flow for this application and express it using Mermaid.",
        "Use a flowchart LR diagram (or another Mermaid type if more appropriate).",
        "Show:",
        "- The user or client",
        "- The frontend (Angular web app)",
        "- The backend (FastAPI)",
        "- The database (MongoDB)",
        "- The AI agents / Claude where relevant",
        "- Key flows between these components.",
        "",
        "IMPORTANT:",
        "- Respond with ONLY valid Mermaid code.",
        "- Do NOT wrap it in ``` fences.",
        "- Do NOT add explanations or comments.",
    ]

    prompt = "\n".join(prompt_sections)

    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=800,
            temperature=0.3,
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        )
    except anthropic.APIError as exc:
        raise HTTPException(
            status_code=500, detail="Claude API error while generating diagram"
        ) from exc

    response_text_parts: List[str] = []
    for block in getattr(response, "content", []):
        if getattr(block, "type", None) == "text" and getattr(block, "text", None):
            response_text_parts.append(block.text)

    mermaid_source = "\n".join(response_text_parts).strip()

    def _strip_fences(text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        if cleaned.lower().startswith("mermaid"):
            cleaned = cleaned[len("mermaid") :].strip()
        return cleaned.strip()

    mermaid_source = _strip_fences(mermaid_source)

    document = {
        "project_id": project_id,
        "diagram_type": "system_flow",
        "mermaid_source": mermaid_source,
        "created_at": datetime.datetime.utcnow(),
    }

    insert_result = await db["diagrams"].insert_one(document)
    document["_id"] = str(insert_result.inserted_id)
    return document

