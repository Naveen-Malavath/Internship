from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import Message

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FeatureSpec:
    title: str
    description: str
    acceptance_criteria: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "acceptanceCriteria": self.acceptance_criteria,
        }

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "FeatureSpec":
        return FeatureSpec(
            title=payload.get("title", "Untitled feature"),
            description=payload.get("description", "No description provided."),
            acceptance_criteria=[
                criterion for criterion in payload.get("acceptanceCriteria", []) if criterion
            ],
        )


@dataclass(slots=True)
class AgentResult:
    run_id: str
    summary: str
    features: list[FeatureSpec]
    debug: dict[str, Any]


@dataclass(slots=True)
class StorySpec:
    feature_title: str
    user_story: str
    acceptance_criteria: list[str]
    implementation_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "featureTitle": self.feature_title,
            "userStory": self.user_story,
            "acceptanceCriteria": self.acceptance_criteria,
            "implementationNotes": self.implementation_notes,
        }

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "StorySpec":
        return StorySpec(
            feature_title=payload.get("featureTitle", "Unknown feature"),
            user_story=payload.get("userStory", "As a user, I want ..."),
            acceptance_criteria=[
                criterion for criterion in payload.get("acceptanceCriteria", []) if criterion
            ],
            implementation_notes=[
                note for note in payload.get("implementationNotes", []) if note
            ],
        )


@dataclass(slots=True)
class AgentStoriesResult:
    run_id: str
    summary: str
    stories: list[StorySpec]
    debug: dict[str, Any]


@dataclass(slots=True)
class VisualizationResult:
    run_id: str
    summary: str
    mermaid: str
    dot: str
    callouts: list[str]
    debug: dict[str, Any]


class ClaudeAgent:
    """Wrapper around Claude 3.5 Haiku for feature ideation."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest") -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_features(self, prompt: str) -> AgentResult:
        run_id = str(uuid.uuid4())
        logger.debug("Agent_1 generating features | run_id=%s", run_id)

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=800,
            temperature=0.4,
            system=(
                "You are Agent_1, a product strategist who translates business ideas into "
                "feature briefs. Respond with concise, implementation-ready suggestions."
                "Always return valid JSON that matches this schema:\n"
                "{\n"
                '  "summary": "one sentence summary",\n'
                '  "features": [\n'
                '    {\n'
                '      "title": "Name the feature",\n'
                '      "description": "Short description (2 sentences max)",\n'
                '      "acceptanceCriteria": ["bullet", "..."]\n'
                "    }\n"
                "  ]\n"
                "}"
            ),
            messages=[
                {"role": "user", "content": [{"type": "text", "text": (
                    "Customer request:\n"
                    f"{prompt}\n\n"
                    "Generate the feature list now."
                )}]}
            ],
        )

        logger.debug(
            "Claude raw response | run_id=%s usage=%s", run_id, getattr(response, "usage", None)
        )

        text = self._extract_text(response)
        payload = self._coerce_json(text)

        features = [
            FeatureSpec(
                title=item.get("title", "Untitled feature"),
                description=item.get("description", "No description provided."),
                acceptance_criteria=[
                    criterion for criterion in item.get("acceptanceCriteria", []) if criterion
                ],
            )
            for item in payload.get("features", [])
        ]

        summary = payload.get("summary", "Feature summary unavailable.")
        debug_payload = {
            "raw_text_preview": text[:250],
        }

        return AgentResult(run_id=run_id, summary=summary, features=features, debug=debug_payload)

    @staticmethod
    def _extract_text(response: Message) -> str:
        parts = []
        for block in response.content:
            if block.type == "text":
                parts.append(block.text)
        return "\n".join(parts).strip()

    @staticmethod
    def _coerce_json(text: str) -> dict[str, Any]:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = stripped.strip("`")
            # Remove language hint if present
            if "\n" in stripped:
                stripped = stripped.split("\n", 1)[1]

        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            logger.warning("Failed to parse Claude JSON. Returning fallback payload.")
            return {
                "summary": stripped[:180],
                "features": [],
            }


class ClaudeStoryAgent:
    """Agent responsible for turning features into implementation-ready stories."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest") -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_stories(self, features: list[FeatureSpec]) -> AgentStoriesResult:
        run_id = str(uuid.uuid4())
        logger.debug("Agent_2 generating stories | run_id=%s features=%d", run_id, len(features))

        feature_outline = "\n".join(
            f"- {feature.title}: {feature.description}" for feature in features
        )

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=900,
            temperature=0.45,
            system=(
                "You are Agent_2, a senior product manager translating feature briefs into user "
                "stories and implementation notes. Always respond with JSON shaped exactly like:\n"
                "{\n"
                '  "summary": "one sentence overview",\n'
                '  "stories": [\n'
                "    {\n"
                '      "featureTitle": "Feature name",\n'
                '      "userStory": "As a ...",\n'
                '      "acceptanceCriteria": ["Given ...", "When ...", "Then ..."],\n'
                '      "implementationNotes": ["first task", "second task"]\n'
                "    }\n"
                "  ]\n"
                "}"
            ),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You will receive a list of features approved by Agent_1.\n"
                                "For each feature, craft a high-quality user story (As a/I want/So that), "
                                "three acceptance criteria, and concrete implementation notes.\n\n"
                                "Approved features:\n"
                                f"{feature_outline}\n\n"
                                "Return the JSON now."
                            ),
                        }
                    ],
                }
            ],
        )

        text = ClaudeAgent._extract_text(response)
        payload = ClaudeAgent._coerce_json(text)

        stories = [
            StorySpec(
                feature_title=item.get("featureTitle", "Unlabelled feature"),
                user_story=item.get("userStory", "As a user, I want ..."),
                acceptance_criteria=[
                    criterion for criterion in item.get("acceptanceCriteria", []) if criterion
                ],
                implementation_notes=[
                    note for note in item.get("implementationNotes", []) if note
                ],
            )
            for item in payload.get("stories", [])
        ]

        summary = payload.get("summary", "Story summary unavailable.")
        debug_payload = {
            "raw_text_preview": text[:250],
        }

        return AgentStoriesResult(
            run_id=run_id,
            summary=summary,
            stories=stories,
            debug=debug_payload,
        )


class ClaudeVisualizationAgent:
    """Agent responsible for producing visual system diagrams from features and stories."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest") -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def generate_visualization(
        self, features: list[FeatureSpec], stories: list[StorySpec]
    ) -> VisualizationResult:
        run_id = str(uuid.uuid4())
        logger.debug(
            "Agent_3 generating visualization | run_id=%s features=%d stories=%d",
            run_id,
            len(features),
            len(stories),
        )

        feature_outline = "\n".join(
            f"- {feature.title}: {feature.description}" for feature in features
        )
        story_outline = "\n".join(
            (
                f"- {story.feature_title}: {story.user_story}\n"
                f"  Acceptance: {', '.join(story.acceptance_criteria)}\n"
                f"  Implementation: {', '.join(story.implementation_notes)}"
            )
            for story in stories
        )

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=900,
            temperature=0.35,
            system=(
                "You are Agent_3, a staff-level product visualizer."
                "Return ONLY JSON with this schema:\n"
                "{\n"
                '  "summary": "overall insight",\n'
                '  "diagrams": {\n'
                '    "mermaid": "Mermaid diagram code",\n'
                '    "dot": "Graphviz DOT diagram"\n'
                "  },\n"
                '  "callouts": ["key insight", "risk", ...]\n'
                "}"
            ),
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Use the following feature briefs and user stories to design"
                                " a system-level diagram.\n\n"
                                "Features:\n"
                                f"{feature_outline or 'None'}\n\n"
                                "Stories:\n"
                                f"{story_outline or 'None'}\n\n"
                                "Ensure the Mermaid output is a flow diagram (graph TD)"
                                " and DOT output is a digraph."
                            ),
                        }
                    ],
                }
            ],
        )

        text = ClaudeAgent._extract_text(response)
        payload = ClaudeAgent._coerce_json(text)

        diagrams = payload.get("diagrams", {}) if isinstance(payload, dict) else {}

        visualization = VisualizationResult(
            run_id=run_id,
            summary=payload.get("summary", "Visualization summary unavailable."),
            mermaid=diagrams.get("mermaid", "graph TD\nA[No data]") if isinstance(diagrams, dict) else "graph TD\nA[No data]",
            dot=diagrams.get("dot", "digraph G { A -> B }") if isinstance(diagrams, dict) else "digraph G { A -> B }",
            callouts=[item for item in payload.get("callouts", []) if isinstance(item, str)],
            debug={
                "raw_text_preview": text[:250],
            },
        )

        return visualization

