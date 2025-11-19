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

    def __init__(self, model: str | None = None) -> None:
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > CLAUDE_MODEL > default
        debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
        if model is None and debug_model:
            self.model = debug_model
            logger.info(f"[agent2] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self.model}")
        else:
            self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
            logger.info(f"[agent2] Initialized with Claude Sonnet 4.5 model: {self.model}")

    async def generate_stories(self, features: List[Dict], original_prompt: str = "") -> List[Dict]:
        """Generate user stories based on provided features and original prompt."""
        logger.info(f"[agent2] Starting story generation with Claude Sonnet 4.5 | model={self.model} | features={len(features)} | prompt_length={len(original_prompt)}")
        if not features:
            logger.warning("[agent2] No features provided, returning empty list")
            return []

        try:
            client = get_claude_client()
            logger.debug("[agent2] Claude client obtained successfully")
        except RuntimeError as exc:
            logger.error(f"[agent2] Failed to get Claude client: {exc}", exc_info=True)
            raise
        
        normalized_features = self._normalize_features(features)
        logger.debug(f"[agent2] Normalized {len(normalized_features)} features")

        feature_outline = "\n".join(
            f"- ID: {feature['id']} Title: {feature['title']}"
            f"\n  Description: {feature['description']}"
            for feature in normalized_features
        )

        # Include original prompt context for better story generation
        prompt_context = ""
        if original_prompt and original_prompt.strip():
            prompt_context = f"\n\nOriginal User Prompt/Requirements:\n{original_prompt.strip()}\n\n"
            prompt_context += "Use this context to ensure stories align with the original user intent and requirements.\n"
        
        user_prompt = (
            "You are Agent-2, a senior product owner. Generate user stories based on features AND the original user prompt.\n"
            "Return JSON:\n"
            "{\n"
            '  "stories": [\n'
            "    {\n"
            '      "feature_id": "Use exact ID from feature list",\n'
            '      "feature_title": "Feature name",\n'
            '      "story_text": "As a ...",\n'
            '      "acceptance_criteria": ["Given ...", "When ...", "Then ..."],\n'
            '      "implementation_notes": ["Component detail", "..."]\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Generate 2-3 stories per feature. Ensure stories relate to both the feature AND the original prompt.\n"
            f"{prompt_context}"
            f"Features:\n{feature_outline}"
        )

        try:
            # Increased max_tokens to prevent truncation of JSON responses with multiple stories per feature
            max_tokens = 4000
            logger.info(f"[agent2] Attempting API call | model={self.model} | max_tokens={max_tokens} | temperature=0.35")
            logger.debug(f"[agent2] User prompt length: {len(user_prompt)} chars")
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.35,  # Lower temperature for faster, more focused responses
                system="Respond ONLY with valid JSON as specified. Be concise.",
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(f"[agent2] API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
            else:
                logger.info("[agent2] API call successful")
        except APIError as exc:
            error_type = getattr(exc, 'type', 'unknown')
            error_status = getattr(exc, 'status_code', None)
            logger.error(f"[agent2] APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
            raise RuntimeError(f"Agent-2 failed to generate stories: {exc}") from exc
        except Exception as exc:
            logger.error(f"[agent2] Unexpected error during API call: {exc}", exc_info=True)
            raise RuntimeError(f"Agent-2 failed to generate stories: {exc}") from exc

        logger.debug("[agent2] Extracting and parsing response")
        try:
            response_text = extract_text(response)
            payload = coerce_json(response_text)
            stories = self._extract_story_payload(payload)
        except RuntimeError as exc:
            logger.error(f"[agent2] Failed to parse response: {exc}", exc_info=True)
            # Try to use fallback instead of failing completely
            logger.warning("[agent2] Using fallback story generation due to parsing error")
            stories = self._fallback_story_payload(normalized_features)
        logger.debug(f"[agent2] Extracted {len(stories)} stories from payload")
        if not stories:
            logger.warning("[agent2] Agent-2 returned no stories. Falling back to heuristic generation.")
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
            final_stories = self._ensure_story_coverage(cleaned, normalized_features)
            logger.info(f"[agent2] Story generation complete | generated={len(final_stories)} stories")
            return final_stories

        logger.warning("[agent2] No cleaned stories, using fallback generation")
        fallback_stories = self._fallback_stories(normalized_features)
        logger.info(f"[agent2] Fallback story generation complete | generated={len(fallback_stories)} stories")
        return fallback_stories

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

        # Use debug model if available, otherwise default
        model = os.getenv("CLAUDE_MODEL_DEBUG") or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
        logger.debug(f"[agent2] generate_stories_for_project using model: {model} for feature: {feature_id_str}")
        
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=1000,
                temperature=0.4,
                messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            )
            usage = getattr(response, "usage", None)
            if usage:
                logger.debug(f"[agent2] generate_stories_for_project API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
        except anthropic.APIError as exc:
            error_type = getattr(exc, 'type', 'unknown')
            error_status = getattr(exc, 'status_code', None)
            logger.error(f"[agent2] generate_stories_for_project APIError - Type: {error_type}, Status: {error_status}, Message: {str(exc)}", exc_info=True)
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

