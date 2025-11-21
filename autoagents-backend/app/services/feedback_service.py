"""Service for handling feedback-based content regeneration."""

import logging
from typing import Any, Dict, Optional

from ..services.agent1 import Agent1Service
from ..services.agent2 import Agent2Service
from ..services.agent3 import Agent3Service

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for regenerating content based on user feedback."""

    def __init__(self):
        logger.debug("[FeedbackService] Initializing feedback service")
        self.agent1_service = Agent1Service()
        self.agent2_service = Agent2Service()
        self.agent3_service = Agent3Service()

    async def regenerate_content(
        self,
        item_id: str,
        item_type: str,
        project_id: str,
        feedback: str,
        original_content: Optional[Dict[str, Any]] = None,
        project_context: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Regenerate content based on feedback."""
        logger.info(
            "[FeedbackService] Regenerating content",
            extra={
                "itemId": item_id,
                "itemType": item_type,
                "projectId": project_id,
                "feedbackLength": len(feedback),
                "hasOriginalContent": bool(original_content),
                "hasProjectContext": bool(project_context),
            },
        )

        try:
            if item_type == "feature":
                return await self._regenerate_feature(
                    item_id, feedback, original_content, project_context
                )
            elif item_type == "story":
                return await self._regenerate_story(
                    item_id, feedback, original_content, project_context
                )
            elif item_type == "visualization":
                return await self._regenerate_visualization(
                    item_id, feedback, original_content, project_context
                )
            else:
                logger.error(
                    "[FeedbackService] Unknown item type",
                    extra={"itemType": item_type},
                )
                raise ValueError(f"Unknown item type: {item_type}")

        except Exception as exc:
            logger.error(
                "[FeedbackService] Error regenerating content",
                exc_info=True,
                extra={"itemId": item_id, "itemType": item_type},
            )
            raise

    async def _regenerate_feature(
        self,
        item_id: str,
        feedback: str,
        original_content: Optional[Dict[str, Any]],
        project_context: Optional[str],
    ) -> Dict[str, Any]:
        """Regenerate a feature based on feedback."""
        logger.debug(
            "[FeedbackService] Regenerating feature",
            extra={"itemId": item_id, "feedbackLength": len(feedback)},
        )

        if not original_content:
            logger.warning(
                "[FeedbackService] No original content provided for feature regeneration",
                extra={"itemId": item_id},
            )
            raise ValueError("Original content is required for feature regeneration")

        project_title = original_content.get("title", "Project")
        project_prompt = project_context or original_content.get("description", "")

        # Build enhanced prompt with feedback
        enhanced_prompt = f"{project_prompt}\n\n=== USER FEEDBACK ===\n{feedback}\n=== END FEEDBACK ===\n\nPlease regenerate this feature incorporating the user's feedback while maintaining alignment with the original project requirements."

        logger.debug(
            "[FeedbackService] Calling Agent1 to regenerate feature",
            extra={
                "itemId": item_id,
                "enhancedPromptLength": len(enhanced_prompt),
            },
        )

        # Call Agent1 with feedback-enhanced prompt
        # Agent1 returns List[str] - feature strings
        features = await self.agent1_service.generate_features(
            project_title=project_title, project_prompt=enhanced_prompt
        )

        if not features or len(features) == 0:
            logger.error(
                "[FeedbackService] Agent1 returned no features",
                extra={"itemId": item_id},
            )
            raise RuntimeError("Failed to regenerate feature: No features returned")

        # Agent1 returns strings, so we need to parse or use the first one
        # For now, use the first feature string and try to extract title/description
        first_feature = features[0] if isinstance(features[0], str) else str(features[0])
        
        # Try to parse "Title: Description" format
        if ":" in first_feature:
            parts = first_feature.split(":", 1)
            title = parts[0].strip()
            description = parts[1].strip() if len(parts) > 1 else ""
        else:
            title = first_feature
            description = ""

        # Return the regenerated feature
        regenerated_feature = {
            "title": title or original_content.get("title", ""),
            "description": description or original_content.get("description", ""),
            "acceptanceCriteria": original_content.get("acceptanceCriteria", []),
        }

        logger.info(
            "[FeedbackService] Feature regenerated successfully",
            extra={"itemId": item_id, "newTitle": regenerated_feature.get("title")},
        )

        return regenerated_feature

    async def _regenerate_story(
        self,
        item_id: str,
        feedback: str,
        original_content: Optional[Dict[str, Any]],
        project_context: Optional[str],
    ) -> Dict[str, Any]:
        """Regenerate a story based on feedback."""
        logger.debug(
            "[FeedbackService] Regenerating story",
            extra={"itemId": item_id, "feedbackLength": len(feedback)},
        )

        if not original_content:
            logger.warning(
                "[FeedbackService] No original content provided for story regeneration",
                extra={"itemId": item_id},
            )
            raise ValueError("Original content is required for story regeneration")

        # Build feature list from original content
        feature_dict = {
            "id": original_content.get("featureTitle", item_id),
            "title": original_content.get("featureTitle", ""),
            "description": original_content.get("description", ""),
        }

        # Build enhanced prompt with feedback
        enhanced_prompt = project_context or ""
        if enhanced_prompt:
            enhanced_prompt += "\n\n"

        enhanced_prompt += f"=== USER FEEDBACK ===\n{feedback}\n=== END FEEDBACK ===\n\nPlease regenerate this user story incorporating the user's feedback while maintaining alignment with the feature and original project requirements."

        logger.debug(
            "[FeedbackService] Calling Agent2 to regenerate story",
            extra={
                "itemId": item_id,
                "enhancedPromptLength": len(enhanced_prompt),
            },
        )

        # Call Agent2 with feedback-enhanced prompt
        # Agent2 returns List[Dict] with story dictionaries
        stories = await self.agent2_service.generate_stories(
            features=[feature_dict], original_prompt=enhanced_prompt
        )

        if not stories or len(stories) == 0:
            logger.error(
                "[FeedbackService] Agent2 returned no stories",
                extra={"itemId": item_id},
            )
            raise RuntimeError("Failed to regenerate story: No stories returned")

        # Agent2 returns list of dicts with keys: feature_id, feature_title, story_text, acceptance_criteria, implementation_notes
        first_story = stories[0]
        
        # Return the first story
        regenerated_story = {
            "featureTitle": first_story.get("feature_title") or first_story.get("feature_id") or original_content.get("featureTitle", ""),
            "userStory": first_story.get("story_text") or first_story.get("user_story") or "",
            "acceptanceCriteria": first_story.get("acceptance_criteria") or [],
            "implementationNotes": first_story.get("implementation_notes") or [],
        }

        logger.info(
            "[FeedbackService] Story regenerated successfully",
            extra={"itemId": item_id},
        )

        return regenerated_story

    async def _regenerate_visualization(
        self,
        item_id: str,
        feedback: str,
        original_content: Optional[Dict[str, Any]],
        project_context: Optional[str],
    ) -> Dict[str, Any]:
        """Regenerate a visualization based on feedback."""
        logger.debug(
            "[FeedbackService] Regenerating visualization",
            extra={"itemId": item_id, "feedbackLength": len(feedback)},
        )

        if not original_content:
            logger.warning(
                "[FeedbackService] No original content provided for visualization regeneration",
                extra={"itemId": item_id},
            )
            raise ValueError(
                "Original content is required for visualization regeneration"
            )

        # Extract features and stories from original content if available
        features = original_content.get("features", [])
        stories = original_content.get("stories", [])
        diagram_type = original_content.get("diagramType", "hld")

        if not features or not stories:
            logger.warning(
                "[FeedbackService] Missing features or stories for visualization regeneration",
                extra={"itemId": item_id, "hasFeatures": bool(features), "hasStories": bool(stories)},
            )
            # Try to use minimal data
            features = features or []
            stories = stories or []

        project_title = original_content.get("projectTitle", "Project")
        original_prompt = project_context or original_content.get("prompt", "")

        # Build enhanced prompt with feedback
        enhanced_prompt = f"{original_prompt}\n\n=== USER FEEDBACK ===\n{feedback}\n=== END FEEDBACK ===\n\nPlease regenerate this diagram incorporating the user's feedback while maintaining alignment with the original project requirements and system architecture."

        logger.debug(
            "[FeedbackService] Calling Agent3 to regenerate visualization",
            extra={
                "itemId": item_id,
                "diagramType": diagram_type,
                "featuresCount": len(features),
                "storiesCount": len(stories),
                "enhancedPromptLength": len(enhanced_prompt),
            },
        )

        # Convert features and stories to the format expected by Agent3
        feature_dicts = [
            {
                "title": f.get("title", ""),
                "feature_text": f.get("title", ""),
                "description": f.get("description", ""),
            }
            for f in features
        ]

        story_dicts = [
            {
                "feature_id": s.get("featureTitle", ""),
                "story_text": s.get("userStory", ""),
                "user_story": s.get("userStory", ""),
                "acceptance_criteria": s.get("acceptanceCriteria", []),
                "implementation_notes": s.get("implementationNotes", []),
            }
            for s in stories
        ]

        # Call Agent3 with feedback-enhanced prompt
        mermaid_diagram = await self.agent3_service.generate_mermaid(
            project_title=project_title,
            features=feature_dicts,
            stories=story_dicts,
            diagram_type=diagram_type,
            original_prompt=enhanced_prompt,
        )

        if not mermaid_diagram:
            logger.error(
                "[FeedbackService] Agent3 returned no diagram",
                extra={"itemId": item_id},
            )
            raise RuntimeError("Failed to regenerate visualization: No diagram returned")

        # Agent3 returns a string (mermaid diagram)
        regenerated_visualization = {
            "mermaid": mermaid_diagram,
            "diagramType": diagram_type,
            "summary": f"Regenerated {diagram_type.upper()} diagram based on user feedback",
            "diagrams": {
                "mermaid": mermaid_diagram,
                "dot": "",  # Agent3 doesn't return DOT, but we include it for compatibility
            },
        }

        logger.info(
            "[FeedbackService] Visualization regenerated successfully",
            extra={"itemId": item_id, "diagramType": diagram_type},
        )

        return regenerated_visualization

