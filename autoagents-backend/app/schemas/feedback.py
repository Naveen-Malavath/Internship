"""Pydantic models for Feedback documents."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    """Request model for feedback submission and regeneration."""

    itemId: str = Field(..., description="ID of the item (feature/story/visualization)")
    itemType: str = Field(..., description="Type of item: 'feature', 'story', or 'visualization'")
    projectId: str = Field(..., description="Project ID")
    feedback: str = Field(..., description="User feedback text")
    originalContent: Optional[Dict[str, Any]] = Field(None, description="Original content to regenerate")
    projectContext: Optional[str] = Field(None, description="Original project prompt/context")
    regenerate: Optional[bool] = Field(False, description="Whether to immediately regenerate")


class FeedbackResponse(BaseModel):
    """Response model for feedback operations."""

    feedbackId: str = Field(..., description="ID of the feedback entry")
    regenerationCount: int = Field(..., description="Current regeneration count for this item")
    autoRegenerate: Optional[bool] = Field(None, description="Whether auto-regeneration was triggered")
    regeneratedContent: Optional[Dict[str, Any]] = Field(None, description="Regenerated content")
    version: Optional[int] = Field(None, description="Version number of regenerated content")
    message: Optional[str] = Field(None, description="Response message")


class FeedbackHistoryEntry(BaseModel):
    """Model for feedback history entries."""

    id: str
    itemId: str
    itemType: str
    feedback: str
    timestamp: str
    status: str  # 'submitted', 'regenerated', 'failed'
    regeneratedAt: Optional[str] = None
    version: Optional[int] = None


class RegenerationCountResponse(BaseModel):
    """Response model for regeneration count query."""

    count: int = Field(..., description="Current regeneration count")


# Chatbot-related schemas
class ChatMessage(BaseModel):
    """Model for a single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="Message timestamp")


class ChatbotRequest(BaseModel):
    """Request model for chatbot interactions."""

    message: str = Field(..., description="User's message to the chatbot")
    conversationId: Optional[str] = Field(None, description="Conversation ID for maintaining context")
    projectId: Optional[str] = Field(None, description="Project ID for context")
    itemId: Optional[str] = Field(None, description="Item ID for context (feature/story/visualization)")
    itemType: Optional[str] = Field(None, description="Type of item: 'feature', 'story', or 'visualization'")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context (item details, etc.)")


class ChatbotResponse(BaseModel):
    """Response model for chatbot interactions."""

    conversationId: str = Field(..., description="Conversation ID")
    messageId: str = Field(..., description="ID of the AI's response message")
    response: str = Field(..., description="AI assistant's response")
    timestamp: str = Field(..., description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (token usage, etc.)")


class FeedbackSuggestionRequest(BaseModel):
    """Request model for feedback improvement suggestions."""

    feedback: str = Field(..., description="Original feedback text")
    itemType: str = Field(..., description="Type of item: 'feature', 'story', or 'visualization'")
    itemContent: Optional[Dict[str, Any]] = Field(None, description="Content of the item being provided feedback on")


class FeedbackSuggestionResponse(BaseModel):
    """Response model for feedback improvement suggestions."""

    suggestions: str = Field(..., description="AI suggestions for improving the feedback")
    originalFeedback: str = Field(..., description="Original feedback text")
    itemType: str = Field(..., description="Type of item")
    messageId: str = Field(..., description="Message ID for tracking")


class RegenerationExplanationRequest(BaseModel):
    """Request model for regeneration explanation."""

    itemType: str = Field(..., description="Type of item that was regenerated")
    originalContent: Dict[str, Any] = Field(..., description="Original content before regeneration")
    regeneratedContent: Dict[str, Any] = Field(..., description="Regenerated content")
    feedback: str = Field(..., description="Feedback that triggered regeneration")


class RegenerationExplanationResponse(BaseModel):
    """Response model for regeneration explanation."""

    explanation: str = Field(..., description="Explanation of what changed and why")
    itemType: str = Field(..., description="Type of item")


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""

    conversationId: str = Field(..., description="Conversation ID")
    messages: List[ChatMessage] = Field(..., description="List of messages in the conversation")
    createdAt: str = Field(..., description="When the conversation was created")
    updatedAt: str = Field(..., description="When the conversation was last updated")
