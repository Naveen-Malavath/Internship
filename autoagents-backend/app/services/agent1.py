"""Agent-1 service responsible for feature generation."""

from __future__ import annotations

import os
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

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)

    async def generate_features(self, project_title: str, project_prompt: str) -> List[str]:
        """Generate feature descriptions for the given project using Claude."""
        try:
            client = get_claude_client()
        except RuntimeError as exc:
            print(f"[agent1] Failed to get Claude client: {exc}")
            raise
        print(f"[agent1] using model {self.model}")

        system_prompt = (
            "You are Agent-1, an AI product manager specializing in translating user ideas and requirements "
            "into comprehensive, actionable feature specifications. Your role is to carefully analyze user input, "
            "understand their vision, and break it down into detailed, implementation-ready features. "
            "Respond ONLY with JSON and the schema:\n"
            "{\n"
            '  "features": [\n'
            '    "Feature description 1",\n'
            '    "Feature description 2"\n'
            "  ]\n"
            "}\n"
            "Provide at least eight implementation-ready feature descriptions that directly address the user's ideas and requirements."
        )
        user_prompt = (
            f"Project title: {project_title or 'Untitled project'}\n"
            f"User's idea/input/prompt:\n{project_prompt or 'No additional prompt provided.'}\n\n"
            "Based on the above user input, generate comprehensive features that:\n"
            "1. Directly address the user's stated needs and goals\n"
            "2. Break down the idea into logical, actionable components\n"
            "3. Cover all major functional areas mentioned in the user's input\n"
            "4. Include both core features and supporting/enhancement features\n"
            "5. Consider user experience, business value, and technical feasibility\n\n"
            "Ensure each feature clearly relates back to the original user idea. "
            "Return the JSON now."
        )

        try:
            print(f"[agent1] attempting API call with model: {self.model}")
            response = await client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.5,
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            print(f"[agent1] API call successful")
        except APIError as exc:  # pragma: no cover - upstream error surface
            print(f"[agent1] APIError: {exc}")
            # If model not found, try fallback to haiku
            if "not_found_error" in str(exc) or "404" in str(exc):
                print(f"[agent1] Model {self.model} not found, trying fallback: claude-3-5-haiku-latest")
                try:
                    response = await client.messages.create(
                        model="claude-3-5-haiku-latest",
                        max_tokens=1200,
                        temperature=0.5,
                        system=system_prompt,
                        messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
                    )
                    print(f"[agent1] Fallback model call successful")
                except APIError as fallback_exc:
                    raise RuntimeError(f"Agent-1 failed with both {self.model} and fallback: {fallback_exc}") from fallback_exc
            else:
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
