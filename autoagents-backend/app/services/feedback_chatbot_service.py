"""Service for handling feedback chatbot interactions using Claude AI."""

import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)


class FeedbackChatbotService:
    """Service for AI-powered feedback chatbot conversations."""

    def __init__(self):
        """Initialize the chatbot service with Claude API."""
        logger.debug("[FeedbackChatbotService] Initializing feedback chatbot service")
        
        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("[FeedbackChatbotService] CLAUDE_API_KEY or ANTHROPIC_API_KEY not found in environment")
            raise ValueError("CLAUDE_API_KEY or ANTHROPIC_API_KEY environment variable is required")
        
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        logger.info(f"[FeedbackChatbotService] Using model: {self._model}")

    async def generate_response(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response to user message.
        
        Args:
            user_message: The user's message
            chat_history: Previous chat messages (list of {role, content} dicts)
            context: Additional context (project info, item details, etc.)
        
        Returns:
            Dictionary with 'response' (AI message), 'message_id', and metadata
        """
        message_id = str(uuid.uuid4())
        logger.info(
            "[FeedbackChatbotService] Generating response",
            extra={
                "messageId": message_id,
                "userMessageLength": len(user_message),
                "historyLength": len(chat_history) if chat_history else 0,
                "hasContext": bool(context),
            },
        )

        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Build messages list
            messages = self._build_messages(user_message, chat_history)
            
            logger.debug(
                f"[FeedbackChatbotService] Calling Claude API | model={self._model} | messages={len(messages)}"
            )
            
            # Call Claude API
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=1024,
                temperature=0.7,
                system=system_prompt,
                messages=messages,
            )
            
            # Extract response text
            ai_response = self._extract_text(response)
            
            # Get token usage
            usage = getattr(response, "usage", None)
            metadata = {}
            if usage:
                metadata = {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                }
                logger.info(
                    f"[FeedbackChatbotService] Response generated | messageId={message_id} | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}"
                )
            else:
                logger.info(f"[FeedbackChatbotService] Response generated | messageId={message_id}")
            
            return {
                "message_id": message_id,
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata,
            }
            
        except Exception as exc:
            logger.error(
                "[FeedbackChatbotService] Error generating response",
                exc_info=True,
                extra={"messageId": message_id},
            )
            raise

    def _build_system_prompt(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Build system prompt for the chatbot."""
        base_prompt = (
            "You are a helpful AI assistant for the AutoAgents platform, specializing in helping users "
            "provide better feedback on their software projects. Your role is to:\n\n"
            "1. Help users articulate clear, actionable feedback for features, user stories, and system diagrams\n"
            "2. Suggest improvements and ask clarifying questions\n"
            "3. Guide users in refining their requirements and acceptance criteria\n"
            "4. Provide insights on software development best practices\n"
            "5. Be concise, professional, and supportive\n\n"
            "When helping with feedback:\n"
            "- Ask specific questions to understand the user's concerns\n"
            "- Suggest concrete improvements\n"
            "- Consider technical feasibility and best practices\n"
            "- Focus on clarity and actionability\n"
        )
        
        # Add context if available
        if context:
            context_lines = []
            
            if context.get("itemType"):
                context_lines.append(f"Current Item Type: {context['itemType']}")
            
            if context.get("projectName"):
                context_lines.append(f"Project: {context['projectName']}")
            
            if context.get("itemTitle"):
                context_lines.append(f"Item: {context['itemTitle']}")
            
            if context.get("itemDescription"):
                context_lines.append(f"Description: {context['itemDescription']}")
            
            if context_lines:
                base_prompt += "\n\nCurrent Context:\n" + "\n".join(context_lines)
        
        return base_prompt

    def _build_messages(
        self,
        user_message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, Any]]:
        """Build messages list for Claude API."""
        messages = []
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Claude API expects 'user' or 'assistant' roles
                if role in ["user", "assistant"]:
                    messages.append({
                        "role": role,
                        "content": content,
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message,
        })
        
        return messages

    @staticmethod
    def _extract_text(response) -> str:
        """Extract text from Claude API response."""
        parts = []
        for block in response.content:
            if block.type == "text":
                parts.append(block.text)
        return "\n".join(parts).strip()

    async def suggest_feedback_improvements(
        self,
        original_feedback: str,
        item_type: str,
        item_content: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Suggest improvements to user's feedback.
        
        Args:
            original_feedback: The user's original feedback text
            item_type: Type of item (feature, story, visualization)
            item_content: The content being provided feedback on
        
        Returns:
            Dictionary with suggestions and improved feedback
        """
        logger.info(
            "[FeedbackChatbotService] Suggesting feedback improvements",
            extra={
                "itemType": item_type,
                "feedbackLength": len(original_feedback),
            },
        )

        try:
            # Build prompt for feedback improvement
            prompt = f"""I have feedback on a {item_type} that I'd like to improve:

Original Feedback:
{original_feedback}

Please provide:
1. Specific suggestions to make this feedback more actionable
2. Questions I should consider
3. An improved version of the feedback

Keep your response concise and practical."""

            # Add item content context if available
            if item_content:
                if item_content.get("title"):
                    prompt = f"Item: {item_content['title']}\n\n" + prompt
                if item_content.get("description"):
                    prompt = f"Description: {item_content['description']}\n\n" + prompt

            # Generate response
            response = await self.generate_response(
                user_message=prompt,
                chat_history=None,
                context={"itemType": item_type},
            )

            return {
                "suggestions": response["response"],
                "original_feedback": original_feedback,
                "item_type": item_type,
                "message_id": response["message_id"],
            }

        except Exception as exc:
            logger.error(
                "[FeedbackChatbotService] Error suggesting improvements",
                exc_info=True,
                extra={"itemType": item_type},
            )
            raise

    async def explain_regeneration(
        self,
        item_type: str,
        original_content: Dict[str, Any],
        regenerated_content: Dict[str, Any],
        feedback: str,
    ) -> str:
        """
        Explain what changed in the regeneration and why.
        
        Args:
            item_type: Type of item that was regenerated
            original_content: Original content before regeneration
            regenerated_content: New content after regeneration
            feedback: The feedback that triggered regeneration
        
        Returns:
            Explanation text
        """
        logger.info(
            "[FeedbackChatbotService] Generating regeneration explanation",
            extra={"itemType": item_type},
        )

        try:
            prompt = f"""I provided feedback on a {item_type}, and it was regenerated. Please explain:
1. What changed between the original and regenerated version
2. How the feedback was incorporated
3. Any potential concerns or suggestions

Original {item_type}:
{self._format_content(original_content)}

Regenerated {item_type}:
{self._format_content(regenerated_content)}

Feedback provided:
{feedback}

Keep the explanation concise and focused on key changes."""

            response = await self.generate_response(
                user_message=prompt,
                chat_history=None,
                context={"itemType": item_type},
            )

            return response["response"]

        except Exception as exc:
            logger.error(
                "[FeedbackChatbotService] Error generating explanation",
                exc_info=True,
                extra={"itemType": item_type},
            )
            raise

    @staticmethod
    def _format_content(content: Dict[str, Any]) -> str:
        """Format content dictionary for display in prompts."""
        lines = []
        
        if content.get("title"):
            lines.append(f"Title: {content['title']}")
        
        if content.get("description"):
            lines.append(f"Description: {content['description']}")
        
        if content.get("userStory"):
            lines.append(f"User Story: {content['userStory']}")
        
        if content.get("acceptanceCriteria"):
            criteria = content["acceptanceCriteria"]
            if isinstance(criteria, list) and criteria:
                lines.append("Acceptance Criteria:")
                for criterion in criteria[:3]:  # Limit to first 3
                    lines.append(f"  - {criterion}")
        
        if content.get("implementationNotes"):
            notes = content["implementationNotes"]
            if isinstance(notes, list) and notes:
                lines.append("Implementation Notes:")
                for note in notes[:3]:  # Limit to first 3
                    lines.append(f"  - {note}")
        
        return "\n".join(lines) if lines else str(content)

