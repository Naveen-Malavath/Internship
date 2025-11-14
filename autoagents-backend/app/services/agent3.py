"""Agent-3 service responsible for Mermaid diagram generation."""

from __future__ import annotations

from typing import Dict, List

from anthropic import APIError

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

