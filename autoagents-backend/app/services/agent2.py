"""Agent-2 service responsible for story generation."""

from __future__ import annotations

import datetime
import logging
import os
from typing import Any, Dict, List

import anthropic
from anthropic import APIError
from fastapi import HTTPException

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    coerce_json,
    extract_text,
    get_claude_client,
)


logger = logging.getLogger(__name__)


class Agent2Service:
    """Service wrapper for generating user stories via Claude."""

    def __init__(self, model: str = DEFAULT_CLAUDE_MODEL) -> None:
        self.model = model

    async def generate_stories(self, features: List[Dict]) -> List[Dict]:
        """Generate user stories based on provided features."""
        if not features:
            return []

        client = get_claude_client()
        normalized_features = self._normalize_features(features)

        feature_outline = "\n".join(
            f"- ID: {feature['id']} Title: {feature['title']}"
            f"\n  Description: {feature['description']}"
            for feature in normalized_features
        )

        user_prompt = (
            "You are Agent-2, a senior product owner. For each feature, return JSON with user stories.\n"
            "{\n"
            '  "stories": [\n'
            "    {\n"
            '      "feature_id": "Use the exact ID provided in the feature list",\n'
            '      "feature_title": "Feature name",\n'
            '      "story_text": "As a ...",\n'
            '      "acceptance_criteria": ["Given ...", "When ...", "Then ..."],\n'
            '      "implementation_notes": ["System component or integration detail", "..."]\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Produce at least two stories per feature, keep acceptance criteria actionable, and include low/medium level implementation notes.\n\n"
            f"Features:\n{feature_outline}"
        )

        try:
            response = await client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.4,
                system="Respond ONLY with JSON as specified.",
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
        except APIError as exc:
            raise RuntimeError(f"Agent-2 failed to generate stories: {exc}") from exc

        payload = coerce_json(extract_text(response))
        stories = self._extract_story_payload(payload)
        if not stories:
            logger.warning("Agent-2 returned no stories. Falling back to heuristic generation.")
            stories = self._fallback_story_payload(normalized_features)

        features_by_id = {feature["id"]: feature for feature in normalized_features}
        features_by_title = {feature["title"].strip().lower(): feature for feature in normalized_features}

        cleaned: List[Dict] = []
        for story in stories:
            feature_data = self._match_feature(story, features_by_id, features_by_title)
            if feature_data is None:
                continue

            story_text = (
                story.get("story_text")
                or story.get("userStory")
                or f"As a user, I want {feature_data['title'].lower()} to drive value."
            )
            acceptance_criteria = self._coerce_list(
                story.get("acceptance_criteria") or story.get("acceptanceCriteria")
            )
            implementation_notes = self._coerce_list(
                story.get("implementation_notes") or story.get("implementationNotes")
            )

            cleaned.append(
                {
                    "feature_id": feature_data["id"],
                    "feature_text": feature_data["title"],
                    "story_text": story_text if isinstance(story_text, str) else "As a user, I want ...",
                    "acceptance_criteria": acceptance_criteria or ["Given ..., When ..., Then ..."],
                    "implementation_notes": implementation_notes,
                }
            )

        if cleaned:
            return self._ensure_story_coverage(cleaned, normalized_features)

        return self._fallback_stories(normalized_features)

    def _extract_story_payload(self, payload: Any) -> List[Dict[str, Any]]:
        """Handle multiple possible payload shapes from Claude."""
        if isinstance(payload, list):
            return [self._coerce_dict(item) for item in payload]

        if isinstance(payload, dict):
            candidate_keys = [
                "stories",
                "Stories",
                "userStories",
                "generatedStories",
                "data",
            ]
            for key in candidate_keys:
                value = payload.get(key)
                if isinstance(value, list):
                    return [self._coerce_dict(item) for item in value]
                if isinstance(value, dict) and "items" in value and isinstance(value["items"], list):
                    return [self._coerce_dict(item) for item in value["items"]]
        return []

    def _normalize_features(self, features: List[Dict]) -> List[Dict[str, Any]]:
        """Normalize heterogeneous feature payloads into a consistent structure."""
        normalized: List[Dict[str, Any]] = []
        seen_ids: set[str] = set()

        for idx, feature in enumerate(features, start=1):
            record = self._coerce_dict(feature)
            detail = self._coerce_dict(record.get("detail"))
            feature_id = (
                record.get("_id")
                or record.get("id")
                or record.get("feature_id")
                or detail.get("key")
                or f"feature-{idx}"
            )
            feature_id = str(feature_id)
            if feature_id in seen_ids:
                feature_id = f"{feature_id}-{idx}"
            seen_ids.add(feature_id)

            title = (
                record.get("feature_text")
                or record.get("title")
                or detail.get("summary")
                or record.get("name")
                or f"Feature {idx}"
            )
            description = (
                record.get("description")
                or record.get("feature_description")
                or detail.get("description")
                or record.get("feature_text")
                or title
            )

            normalized.append(
                {
                    "id": feature_id,
                    "title": str(title).strip() or f"Feature {idx}",
                    "description": str(description).strip() or str(title).strip() or f"Feature {idx}",
                }
            )

        return normalized

    def _match_feature(
        self,
        story: Dict[str, Any],
        features_by_id: Dict[str, Dict[str, Any]],
        features_by_title: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any] | None:
        """Attempt to map a story back to a known feature."""
        feature_ref = (
            story.get("feature_id")
            or story.get("featureId")
            or story.get("feature_title")
            or story.get("featureTitle")
        )
        feature_title = (
            story.get("feature_text")
            or story.get("featureTitle")
            or story.get("feature_title")
        )

        if feature_ref:
            ref = str(feature_ref).strip()
            match = features_by_id.get(ref) or features_by_title.get(ref.lower())
            if match:
                return match

        if feature_title:
            ref = str(feature_title).strip().lower()
            match = features_by_title.get(ref)
            if match:
                return match

        # If the model didn't pick a feature, fall back to the first available.
        return next(iter(features_by_id.values()), None)

    def _ensure_story_coverage(
        self,
        stories: List[Dict[str, Any]],
        features: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Ensure every feature receives at least one story."""
        covered_ids = {
            story.get("feature_id")
            for story in stories
            if story.get("feature_id")
        }
        missing = [feature for feature in features if feature["id"] not in covered_ids]
        if not missing:
            return stories

        logger.info("Agent-2 missing stories for %d feature(s); adding placeholders.", len(missing))
        return stories + self._fallback_story_payload(missing)

    def _fallback_story_payload(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate placeholder stories when Claude fails to respond."""
        return [self._build_placeholder_story(feature) for feature in features]

    def _coerce_list(self, value: Any) -> List[str]:
        """Ensure acceptance criteria / implementation notes are simple string lists."""
        if not value:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()]

    def _coerce_dict(self, value: Any) -> Dict[str, Any]:
        """Best-effort conversion to dict for incoming feature payloads."""
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        if hasattr(value, "__dict__"):
            return dict(value.__dict__)
        return {}

    def _fallback_stories(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate deterministic placeholder stories if Claude returns nothing."""
        fallback: List[Dict[str, Any]] = []
        for index, feature in enumerate(features, start=1):
            title = feature["title"]
            description = feature["description"]
            story_text = (
                f"As a stakeholder, I want {title.lower()} so we can deliver {description.lower()}."
            )
            fallback.append(
                {
                    "feature_id": feature["id"],
                    "feature_text": title,
                    "story_text": story_text,
                    "acceptance_criteria": [
                        f"Given the team is planning {title.lower()}, when we scope the work, then we document the detailed tasks.",
                        f"Given the feature requires measurable outcomes, when we review {title.lower()}, then we confirm success metrics.",
                    ],
                    "implementation_notes": [
                        "Placeholder story generated locally because Agent 2 returned no data.",
                        "Replace with refined stories once Agent 2 is reachable.",
                    ],
                }
            )
        return fallback

    def _build_placeholder_story(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Create a deterministic placeholder story for a specific feature."""
        title = feature["title"]
        description = feature["description"]
        normalized_title = title.lower()
        normalized_description = description.lower()
        return {
            "feature_id": feature["id"],
            "feature_text": title,
            "story_text": f"As a user, I want {normalized_title} so that {normalized_description}",
            "acceptance_criteria": [
                f"Given {title}, when the capability is triggered, then value is delivered.",
                "Given authenticated access, when roles are enforced, then data remains protected.",
                "Given monitoring hooks, when events occur, then stakeholders receive alerts.",
            ],
            "implementation_notes": [
                "Coordinate with backend/API owners.",
                "Capture telemetry for success metrics.",
            ],
        }


async def generate_stories_for_project(project_id: str, db):
    """Generate and persist user stories for all features in a project."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Claude API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    if not features:
        raise HTTPException(
            status_code=400, detail="No features found for this project. Run Agent-1 first."
        )

    created_stories: List[Dict[str, Any]] = []

    for feature in features:
        feature_text = feature.get("feature_text") or ""
        feature_id_str = str(feature.get("_id")) if feature.get("_id") is not None else ""

        prompt = (
            "You are an expert Agile business analyst.\n\n"
            f"Feature: {feature_text}\n\n"
            "Task:\n"
            "Write 2–3 user stories in this exact format:\n"
            '"As a <type of user>, I want <goal> so that <reason>."\n\n'
            "For each user story, write 2–3 acceptance criteria as bullet points.\n\n"
            "Return the result as plain text, with a blank line between each user story."
        )

        try:
            response = await client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=1000,
                temperature=0.4,
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            )
        except anthropic.APIError as exc:
            raise HTTPException(
                status_code=500, detail="Claude API error while generating user stories"
            ) from exc

        response_text_parts: List[str] = []
        for block in getattr(response, "content", []):
            if getattr(block, "type", None) == "text" and getattr(block, "text", None):
                response_text_parts.append(block.text)
        response_text = "\n".join(response_text_parts).strip()
        if not response_text:
            continue

        story_blocks = [block.strip() for block in response_text.split("\n\n") if block.strip()]

        for block in story_blocks:
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if not lines:
                continue

            story_text = lines[0]
            acceptance_criteria = "\n".join(lines[1:]) if len(lines) > 1 else ""

            document = {
                "project_id": project_id,
                "feature_id": feature_id_str,
                "story_text": story_text,
                "acceptance_criteria": acceptance_criteria,
                "created_at": datetime.datetime.utcnow(),
            }

            insert_result = await db["stories"].insert_one(document)
            stored_doc = {**document, "_id": str(insert_result.inserted_id)}
            created_stories.append(stored_doc)

    return created_stories

