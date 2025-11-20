from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import dataclass
from typing import Any

from anthropic import AsyncAnthropic
from anthropic.types import Message

from .services.claude_client import (
    DEFAULT_CLAUDE_MODEL,
    coerce_json,
    extract_text,
)

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
    """Wrapper around Claude Sonnet 4.5 for feature ideation."""

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > DEFAULT_CLAUDE_MODEL
        if model is None:
            debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
            if debug_model:
                self._model = debug_model
                logger.info(f"[ClaudeAgent] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self._model}")
            else:
                self._model = DEFAULT_CLAUDE_MODEL
                logger.info(f"[ClaudeAgent] Using default Sonnet 4.5 model: {self._model}")
        else:
            self._model = model
            logger.info(f"[ClaudeAgent] Using explicit model: {self._model}")

    async def generate_features(self, prompt: str) -> AgentResult:
        run_id = str(uuid.uuid4())
        logger.info(f"[ClaudeAgent] Starting feature generation | run_id={run_id} | model={self._model} | prompt_length={len(prompt)}")

        logger.debug(f"[ClaudeAgent] Attempting API call | model={self._model} | max_tokens=1400 | temperature=0.4")
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1400,
            temperature=0.4,
            system=(
                "You are Agent_1, a product strategist who translates business ideas into "
                "feature briefs. Respond with concise, implementation-ready suggestions. "
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
                "}\n"
                'Ensure the "features" array contains at least eight distinct items spanning onboarding, core workflows, administration/compliance, analytics/reporting, integrations, and forward-looking innovation. '
                "Keep the prose tight so everything fits within the token budget."
            ),
            messages=[
                {"role": "user", "content": [{"type": "text", "text": (
                    "Customer request:\n"
                    f"{prompt}\n\n"
                    "Generate the feature list now."
                )}]}
            ],
        )

        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[ClaudeAgent] API call successful | run_id={run_id} | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
        else:
            logger.info(f"[ClaudeAgent] API call successful | run_id={run_id}")

        logger.debug(f"[ClaudeAgent] Extracting and parsing response | run_id={run_id}")
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
        
        logger.info(f"[ClaudeAgent] Feature generation complete | run_id={run_id} | generated={len(features)} features")
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

        decoder = json.JSONDecoder()
        try:
            payload, _ = decoder.raw_decode(stripped)
            return payload
        except json.JSONDecodeError:
            pass

        first_brace = stripped.find("{")
        last_brace = stripped.rfind("}")
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            candidate = stripped[first_brace : last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                logger.debug("Candidate JSON slice failed to parse; continuing fallback.", exc_info=True)

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

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > DEFAULT_CLAUDE_MODEL
        if model is None:
            debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
            if debug_model:
                self._model = debug_model
                logger.info(f"[ClaudeStoryAgent] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self._model}")
            else:
                self._model = DEFAULT_CLAUDE_MODEL
                logger.info(f"[ClaudeStoryAgent] Using default Sonnet 4.5 model: {self._model}")
        else:
            self._model = model
            logger.info(f"[ClaudeStoryAgent] Using explicit model: {self._model}")

    async def generate_stories(self, features: list[FeatureSpec]) -> AgentStoriesResult:
        run_id = str(uuid.uuid4())
        logger.info(f"[ClaudeStoryAgent] Starting story generation | run_id={run_id} | model={self._model} | features={len(features)}")

        feature_outline = "\n".join(
            f"- {feature.title}: {feature.description}" for feature in features
        )

        logger.debug(f"[ClaudeStoryAgent] Attempting API call | model={self._model} | max_tokens=1400 | temperature=0.4")
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1400,
            temperature=0.4,
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
                "}\n"
                "Return at least eight story objects for every approved feature (match exactly by featureTitle). "
                "Ensure acceptance criteria include low- and medium-level architectural considerations. "
                "Keep prose concise so the response stays within the token budget."
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

        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[ClaudeStoryAgent] API call successful | run_id={run_id} | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
        else:
            logger.info(f"[ClaudeStoryAgent] API call successful | run_id={run_id}")
        
        logger.debug(f"[ClaudeStoryAgent] Extracting and parsing response | run_id={run_id}")
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
        if not stories:
            logger.warning("Agent_2 returned no stories. Falling back to generated scaffolding.")
            stories = []
            for feature in features:
                stories.append(self._build_placeholder_story(feature))
            summary = (
                summary
                if summary and summary != "Story summary unavailable."
                else "Generated placeholder stories because Agent_2 response was empty."
            )
        debug_payload = {
            "raw_text_preview": text[:250],
        }
        
        logger.info(f"[ClaudeStoryAgent] Story generation complete | run_id={run_id} | generated={len(stories)} stories")
        return AgentStoriesResult(run_id=run_id, summary=summary, stories=stories, debug=debug_payload)

    def _build_placeholder_story(self, feature: FeatureSpec) -> StorySpec:
        title = feature.title or "Unlabelled feature"
        user_story = (
            f"As a platform engineer, I need {title.lower()} capabilities so that the solution stays reliable."
        )
        acceptance = [
            f"Given the {title.lower()} service is provisioned, when a workload executes, then end-to-end tracing is captured.",
            f"Given deployment pipelines run for {title.lower()}, when artifacts are promoted, then infrastructure policies pass.",
            f"Given observability hooks are enabled, when {title.lower()} integrates with downstream systems, then alerts trigger within service budgets.",
        ]
        implementation = [
            f"Outline modules, interfaces, and data contracts for the {title.lower()} stack.",
            "Integrate shared authentication, logging, and metrics components.",
            "Automate integration tests covering API, data, and messaging flows.",
        ]
        return StorySpec(
            feature_title=title,
            user_story=user_story,
            acceptance_criteria=acceptance,
            implementation_notes=implementation,
        )


class ClaudeVisualizationAgent:
    """Agent responsible for producing visual system diagrams from features and stories."""

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > DEFAULT_CLAUDE_MODEL
        if model is None:
            debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
            if debug_model:
                self._model = debug_model
                logger.info(f"[ClaudeVisualizationAgent] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self._model}")
            else:
                self._model = DEFAULT_CLAUDE_MODEL
                logger.info(f"[ClaudeVisualizationAgent] Using default Sonnet 4.5 model: {self._model}")
        else:
            self._model = model
            logger.info(f"[ClaudeVisualizationAgent] Using explicit model: {self._model}")

    async def generate_visualization(
        self, features: list[FeatureSpec], stories: list[StorySpec]
    ) -> VisualizationResult:
        run_id = str(uuid.uuid4())
        logger.info(
            f"[ClaudeVisualizationAgent] Starting visualization generation | run_id={run_id} | model={self._model} | features={len(features)} | stories={len(stories)}"
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

        # Optimized max_tokens for faster responses
        logger.debug(f"[ClaudeVisualizationAgent] Attempting API call | model={self._model} | max_tokens=1200 | temperature=0.3")
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=1200,  # Increased slightly but still optimized
            temperature=0.3,  # Lower temperature for faster responses
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

        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[ClaudeVisualizationAgent] API call successful | run_id={run_id} | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
        else:
            logger.info(f"[ClaudeVisualizationAgent] API call successful | run_id={run_id}")
        
        logger.debug(f"[ClaudeVisualizationAgent] Extracting and parsing response | run_id={run_id}")
        try:
            text = extract_text(response)
            logger.debug(f"[ClaudeVisualizationAgent] Extracted response text: {len(text)} chars | preview: {text[:200]}...")
        except RuntimeError as exc:
            logger.error(f"[ClaudeVisualizationAgent] Failed to extract text from response: {exc}", exc_info=True)
            raise RuntimeError(f"Failed to extract response from Claude API: {exc}") from exc
        
        try:
            payload = coerce_json(text)
            logger.debug(f"[ClaudeVisualizationAgent] Successfully parsed JSON: type={type(payload)} | keys={list(payload.keys()) if isinstance(payload, dict) else 'N/A'}")
        except RuntimeError as exc:
            logger.error(f"[ClaudeVisualizationAgent] Failed to parse JSON from response: {exc}", exc_info=True)
            logger.debug(f"[ClaudeVisualizationAgent] Raw response text that failed (first 500): {text[:500]}")
            logger.debug(f"[ClaudeVisualizationAgent] Raw response text that failed (last 500): {text[-500:] if len(text) > 500 else text}")
            # Don't return fallback - raise error so caller knows it failed
            raise RuntimeError(f"Failed to parse Claude JSON response: {exc}") from exc

        # Validate payload structure
        if not isinstance(payload, dict):
            logger.error(f"[ClaudeVisualizationAgent] Payload is not a dict: type={type(payload)} | value={str(payload)[:200]}")
            raise RuntimeError(f"Claude returned invalid response format. Expected dict, got {type(payload)}")
        
        diagrams = payload.get("diagrams", {})
        if not isinstance(diagrams, dict):
            logger.warning(f"[ClaudeVisualizationAgent] Diagrams is not a dict: type={type(diagrams)}, using empty dict")
            diagrams = {}
        
        mermaid_raw = diagrams.get("mermaid", "")
        dot_raw = diagrams.get("dot", "")
        
        # Validate mermaid and dot are non-empty strings
        mermaid = mermaid_raw.strip() if isinstance(mermaid_raw, str) and mermaid_raw.strip() else "graph TD\nA[No data]"
        dot = dot_raw.strip() if isinstance(dot_raw, str) and dot_raw.strip() else "digraph G { A -> B }"
        
        logger.debug(f"[ClaudeVisualizationAgent] Extracted diagrams - mermaid: {len(mermaid)} chars, dot: {len(dot)} chars")
        if mermaid and mermaid != "graph TD\nA[No data]":
            logger.debug(f"[ClaudeVisualizationAgent] Mermaid preview: {mermaid[:150]}...")
        if dot and dot != "digraph G { A -> B }":
            logger.debug(f"[ClaudeVisualizationAgent] DOT preview: {dot[:150]}...")
        
        summary = payload.get("summary", "")
        if not summary or not isinstance(summary, str):
            logger.warning(f"[ClaudeVisualizationAgent] Summary is missing or invalid, using default")
            summary = "Visualization summary unavailable."
        
        callouts = payload.get("callouts", [])
        if not isinstance(callouts, list):
            logger.warning(f"[ClaudeVisualizationAgent] Callouts is not a list: type={type(callouts)}, using empty list")
            callouts = []
        callouts = [item for item in callouts if isinstance(item, str)]
        
        visualization = VisualizationResult(
            run_id=run_id,
            summary=summary,
            mermaid=mermaid,
            dot=dot,
            callouts=callouts,
            debug={
                "raw_text_preview": text[:250],
                "payload_keys": list(payload.keys()) if isinstance(payload, dict) else [],
            },
        )
        
        logger.info(f"[ClaudeVisualizationAgent] Visualization generation complete | run_id={run_id} | mermaid_length={len(visualization.mermaid)} | dot_length={len(visualization.dot)}")
        return visualization


class ClaudeSuggestionAgent:
    """Agent responsible for generating project suggestions like summaries, epics, acceptance criteria, and risks."""

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > DEFAULT_CLAUDE_MODEL
        if model is None:
            debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
            if debug_model:
                self._model = debug_model
                logger.info(f"[ClaudeSuggestionAgent] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self._model}")
            else:
                self._model = DEFAULT_CLAUDE_MODEL
                logger.info(f"[ClaudeSuggestionAgent] Using default Sonnet 4.5 model: {self._model}")
        else:
            self._model = model
            logger.info(f"[ClaudeSuggestionAgent] Using explicit model: {self._model}")

    async def generate_suggestion(
        self, 
        suggestion_type: str,
        prompt: str,
        project_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Generate AI suggestions based on type.
        
        Args:
            suggestion_type: One of 'summary', 'epics', 'acceptanceCriteria', 'stories' (for risks)
            prompt: The base prompt template
            project_context: Optional project details (industry, methodology, etc.)
        
        Returns:
            Dictionary with 'output' (text) and 'run_id'
        """
        run_id = str(uuid.uuid4())
        logger.debug("SuggestionAgent generating %s | run_id=%s", suggestion_type, run_id)

        # Build context-aware prompt
        context_lines = []
        if project_context:
            if project_context.get("industry"):
                context_lines.append(f"Industry: {project_context['industry']}")
            if project_context.get("methodology"):
                context_lines.append(f"Methodology: {project_context['methodology']}")
            if project_context.get("name"):
                context_lines.append(f"Project Name: {project_context['name']}")
            if project_context.get("description"):
                context_lines.append(f"Project Description: {project_context['description']}")
            if project_context.get("focusAreas"):
                focus_areas = project_context["focusAreas"]
                if isinstance(focus_areas, list):
                    context_lines.append(f"Focus Areas: {', '.join(focus_areas)}")
                else:
                    context_lines.append(f"Focus Areas: {focus_areas}")

        # Replace placeholders in prompt
        final_prompt = prompt
        if project_context:
            final_prompt = final_prompt.replace("{industry}", project_context.get("industry", "General"))
            final_prompt = final_prompt.replace("{methodology}", project_context.get("methodology", "scrum"))
            if "{focusAreas}" in final_prompt:
                focus_areas = project_context.get("focusAreas", [])
                if isinstance(focus_areas, list):
                    focus_str = ", ".join(focus_areas)
                else:
                    focus_str = str(focus_areas)
                final_prompt = final_prompt.replace("{focusAreas}", focus_str)

        # Build system prompt based on suggestion type
        system_prompts = {
            "summary": (
                "You are a product strategist drafting executive summaries for project initiatives. "
                "Respond with a concise, professional executive summary (under 120 words) that highlights "
                "customer impact and business outcomes. Return ONLY the summary text, no JSON, no markdown formatting."
            ),
            "epics": (
                "You are a product manager creating epic-level roadmap initiatives. "
                "Respond with 4-6 epic ideas, each on a new line, formatted as: 'Epic N: [Title] - [One sentence justification]'. "
                "Return ONLY the epic list, one per line, no JSON, no markdown formatting."
            ),
            "acceptanceCriteria": (
                "You are a product owner defining acceptance criteria for MVP releases. "
                "Respond with key acceptance criteria as bullet points, one per line, starting with '- '. "
                "Return ONLY the criteria list, no JSON, no markdown formatting."
            ),
            "stories": (  # Used for risk register
                "You are a delivery manager identifying project risks. "
                "Respond with the top delivery risks, one per line, formatted as: '- [Risk description]'. "
                "Cover technology, compliance, and people considerations. "
                "Return ONLY the risk list, no JSON, no markdown formatting."
            ),
        }

        system_prompt = system_prompts.get(suggestion_type, system_prompts["summary"])

        # Build user message
        user_message_parts = []
        if context_lines:
            user_message_parts.append("Project Context:")
            user_message_parts.extend(context_lines)
            user_message_parts.append("")
        user_message_parts.append(final_prompt)

        logger.debug(f"[ClaudeSuggestionAgent] Attempting API call | model={self._model} | type={suggestion_type} | max_tokens=800 | temperature=0.4")
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=800,
            temperature=0.4,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "\n".join(user_message_parts)}]
                }
            ],
        )

        usage = getattr(response, "usage", None)
        if usage:
            logger.info(f"[ClaudeSuggestionAgent] API call successful | run_id={run_id} | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
        else:
            logger.info(f"[ClaudeSuggestionAgent] API call successful | run_id={run_id}")
        
        logger.debug(f"[ClaudeSuggestionAgent] Extracting response | run_id={run_id}")
        text = ClaudeAgent._extract_text(response)
        
        # Clean up the response (remove markdown formatting if present)
        cleaned_text = text.strip()
        if cleaned_text.startswith("```"):
            # Remove code blocks
            lines = cleaned_text.split("\n")
            if len(lines) > 1:
                cleaned_text = "\n".join(lines[1:-1]).strip()
        # Remove any leading dashes/bullets if they're duplicated
        cleaned_text = cleaned_text.strip()

        logger.info(
            f"[ClaudeSuggestionAgent] Suggestion generation complete | run_id={run_id} | type={suggestion_type} | length={len(cleaned_text)}"
        )

        return {
            "run_id": run_id,
            "output": cleaned_text,
            "type": suggestion_type,
        }

