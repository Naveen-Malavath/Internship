"""Agent-1 service responsible for feature generation."""

from __future__ import annotations

from datetime import datetime
from typing import List

from anthropic import APIError
from bson import ObjectId
from fastapi import HTTPException, status

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    coerce_json,
    extract_text,
    get_claude_client,
)


class Agent1Service:
    """Service wrapper for generating features via Claude."""

    def __init__(self, model: str = DEFAULT_CLAUDE_MODEL) -> None:
        self.model = model

    async def generate_features(self, project_title: str, project_prompt: str) -> List[str]:
        """Generate feature descriptions for the given project using Claude."""
        client = get_claude_client()
        print(f"[agent1] using model {self.model}")

        system_prompt = (
            "You are Agent-1, an AI product manager. Respond ONLY with JSON and the schema:\n"
            "{\n"
            '  "features": [\n'
            '    "Feature description 1",\n'
            '    "Feature description 2"\n'
            "  ]\n"
            "}\n"
            "Provide at least eight implementation-ready feature descriptions."
        )
        user_prompt = (
            f"Project title: {project_title or 'Untitled project'}\n"
            f"Project prompt:\n{project_prompt or 'No additional prompt provided.'}\n"
            "Return the JSON now."
        )

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.5,
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
        except APIError as exc:  # pragma: no cover - upstream error surface
            raise RuntimeError(f"Agent-1 failed to generate features: {exc}") from exc

        payload = coerce_json(extract_text(response))
        features = payload.get("features", [])
        if not isinstance(features, list):
            raise RuntimeError("Agent-1 returned an unexpected payload.")

        return [feature for feature in features if isinstance(feature, str) and feature.strip()]


async def generate_features_for_project(project_id: str, db) -> List[dict]:
    """Generate and persist features for a project using Claude."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    service = Agent1Service()
    try:
        feature_texts = await service.generate_features(
            project_title=project.get("title", ""),
            project_prompt=project.get("prompt", ""),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    now = datetime.utcnow()
    documents = [
        {
            "project_id": project_id,
            "feature_text": text.strip(),
            "order_index": index,
            "created_at": now,
        }
        for index, text in enumerate(feature_texts, start=1)
    ]

    if not documents:
        return []

    result = await db["features"].insert_many(documents)
    inserted = []
    for document, inserted_id in zip(documents, result.inserted_ids, strict=False):
        document["_id"] = str(inserted_id)
        inserted.append(document)

    return inserted
