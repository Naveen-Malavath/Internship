"""Feedback endpoints for AutoAgents backend."""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import ValidationError

from ..db import get_database
from ..schemas.feedback import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackHistoryEntry,
    RegenerationCountResponse,
    ChatbotRequest,
    ChatbotResponse,
    FeedbackSuggestionRequest,
    FeedbackSuggestionResponse,
    RegenerationExplanationRequest,
    RegenerationExplanationResponse,
    ConversationHistoryResponse,
    ChatMessage,
)
from ..services.feedback_service import FeedbackService
from ..services.feedback_chatbot_service import FeedbackChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Initialize feedback services
feedback_service = FeedbackService()
chatbot_service = FeedbackChatbotService()


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Submit feedback for a feature, story, or visualization."""
    logger.debug(
        "[feedback] Submitting feedback",
        extra={
            "itemId": request.itemId,
            "itemType": request.itemType,
            "projectId": request.projectId,
            "feedbackLength": len(request.feedback),
        },
    )

    try:
        # Validate request
        if not request.itemId or not request.itemType or not request.feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: itemId, itemType, or feedback",
            )

        if request.itemType not in ["feature", "story", "visualization"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid itemType: {request.itemType}. Must be 'feature', 'story', or 'visualization'",
            )

        db = get_database()
        feedback_id = str(uuid.uuid4())

        # Create feedback history entry
        feedback_entry = {
            "_id": feedback_id,
            "item_id": request.itemId,
            "item_type": request.itemType,
            "project_id": request.projectId,
            "feedback": request.feedback,
            "original_content": request.originalContent,
            "project_context": request.projectContext,
            "status": "submitted",
            "created_at": datetime.utcnow(),
            "version": 0,
        }

        logger.debug(
            "[feedback] Creating feedback entry",
            extra={"feedbackId": feedback_id, "itemId": request.itemId},
        )

        # Insert into database
        await db["feedback_history"].insert_one(feedback_entry)

        # Get current regeneration count
        regeneration_count = await _get_regeneration_count(
            db, request.itemId, request.itemType
        )

        # ✅ AUTO-REGENERATE CONTENT BASED ON FEEDBACK
        logger.info("[feedback] Auto-regenerating content based on feedback")
        
        try:
            regenerated_content = await feedback_service.regenerate_content(
                item_id=request.itemId,
                item_type=request.itemType,
                project_id=request.projectId,
                feedback=request.feedback,
                original_content=request.originalContent,
                project_context=request.projectContext,
            )
            
            if regenerated_content:
                # Update feedback entry with regenerated content
                new_regeneration_count = regeneration_count + 1
                await db["feedback_history"].update_one(
                    {"_id": feedback_id},
                    {
                        "$set": {
                            "status": "regenerated",
                            "regenerated_at": datetime.utcnow(),
                            "version": new_regeneration_count,
                            "regenerated_content": regenerated_content,
                        }
                    },
                )
                
                logger.info(
                    "[feedback] Feedback submitted and content regenerated successfully",
                    extra={
                        "feedbackId": feedback_id,
                        "itemId": request.itemId,
                        "itemType": request.itemType,
                        "regenerationCount": new_regeneration_count,
                    },
                )
                
                return FeedbackResponse(
                    feedbackId=feedback_id,
                    regenerationCount=new_regeneration_count,
                    regeneratedContent=regenerated_content,  # ✅ Return regenerated content
                    version=new_regeneration_count,
                    autoRegenerate=True,  # ✅ Set to true
                    message="Feedback submitted and content regenerated successfully",
                )
        except Exception as regen_error:
            logger.error(
                "[feedback] Failed to auto-regenerate content",
                exc_info=True,
                extra={"feedbackId": feedback_id, "error": str(regen_error)},
            )
            # Still return success for feedback submission, but without regeneration
            return FeedbackResponse(
                feedbackId=feedback_id,
                regenerationCount=regeneration_count,
                autoRegenerate=False,
                message="Feedback submitted successfully, but regeneration failed. Please try regenerating manually.",
            )

        # Fallback return (should not reach here)
        logger.info(
            "[feedback] Feedback submitted successfully (no regeneration attempted)",
            extra={
                "feedbackId": feedback_id,
                "itemId": request.itemId,
                "itemType": request.itemType,
                "regenerationCount": regeneration_count,
            },
        )

        return FeedbackResponse(
            feedbackId=feedback_id,
            regenerationCount=regeneration_count,
            autoRegenerate=False,
            message="Feedback submitted successfully",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "[feedback] Error submitting feedback",
            exc_info=True,
            extra={"itemId": request.itemId, "itemType": request.itemType},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit feedback: {str(exc)}",
        ) from exc


@router.post("/regenerate", response_model=FeedbackResponse)
async def regenerate_content(request: FeedbackRequest) -> FeedbackResponse:
    """Regenerate content based on feedback."""
    logger.debug(
        "[feedback] Regenerating content",
        extra={
            "itemId": request.itemId,
            "itemType": request.itemType,
            "projectId": request.projectId,
            "hasFeedback": bool(request.feedback),
        },
    )

    try:
        # Validate request
        if not request.itemId or not request.itemType:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required fields: itemId or itemType",
            )

        db = get_database()

        # Get current regeneration count for tracking
        regeneration_count = await _get_regeneration_count(
            db, request.itemId, request.itemType
        )

        logger.debug(
            "[feedback] Current regeneration count",
            extra={
                "itemId": request.itemId,
                "itemType": request.itemType,
                "count": regeneration_count,
            },
        )

        # Get latest feedback for this item
        latest_feedback = await db["feedback_history"].find_one(
            {"item_id": request.itemId, "item_type": request.itemType},
            sort=[("created_at", -1)],
        )

        if not latest_feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No feedback found for this item",
            )

        feedback_text = request.feedback or latest_feedback.get("feedback", "")

        logger.debug(
            "[feedback] Calling feedback service to regenerate",
            extra={
                "itemId": request.itemId,
                "itemType": request.itemType,
                "feedbackLength": len(feedback_text),
            },
        )

        # Call feedback service to regenerate content
        regenerated_content = await feedback_service.regenerate_content(
            item_id=request.itemId,
            item_type=request.itemType,
            project_id=request.projectId,
            feedback=feedback_text,
            original_content=request.originalContent or latest_feedback.get("original_content"),
            project_context=request.projectContext or latest_feedback.get("project_context"),
        )

        if not regenerated_content:
            logger.error(
                "[feedback] Regeneration returned no content",
                extra={"itemId": request.itemId, "itemType": request.itemType},
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "code": "LLM_FAILURE",
                    "message": "Failed to regenerate content. The AI service encountered an error.",
                },
            )

        # Increment regeneration count
        new_regeneration_count = regeneration_count + 1

        # Update feedback entry
        await db["feedback_history"].update_one(
            {"_id": latest_feedback["_id"]},
            {
                "$set": {
                    "status": "regenerated",
                    "regenerated_at": datetime.utcnow(),
                    "version": new_regeneration_count,
                    "regenerated_content": regenerated_content,
                }
            },
        )

        logger.info(
            "[feedback] Content regenerated successfully",
            extra={
                "itemId": request.itemId,
                "itemType": request.itemType,
                "newCount": new_regeneration_count,
                "version": new_regeneration_count,
            },
        )

        return FeedbackResponse(
            feedbackId=str(latest_feedback["_id"]),
            regenerationCount=new_regeneration_count,
            regeneratedContent=regenerated_content,
            version=new_regeneration_count,
            message="Content regenerated successfully",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "[feedback] Error regenerating content",
            exc_info=True,
            extra={"itemId": request.itemId, "itemType": request.itemType},
        )

        error_code = "REGENERATION_FAILED"
        error_message = "Failed to regenerate content. Please try again."

        if "LLM" in str(exc).upper() or "API" in str(exc).upper():
            error_code = "LLM_FAILURE"
            error_message = "The AI service encountered an error. Please try again in a moment."

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": error_code, "message": error_message},
        ) from exc


@router.get("/history/{item_id}", response_model=List[FeedbackHistoryEntry])
async def get_feedback_history(
    item_id: str, itemType: str = Query(..., description="Type of item: 'feature', 'story', or 'visualization'")
) -> List[FeedbackHistoryEntry]:
    """Get feedback history for an item."""
    logger.debug(
        "[feedback] Getting feedback history",
        extra={"itemId": item_id, "itemType": itemType},
    )

    try:
        db = get_database()

        cursor = db["feedback_history"].find(
            {"item_id": item_id, "item_type": itemType}
        ).sort("created_at", -1)

        entries = await cursor.to_list(length=50)  # Limit to 50 most recent

        logger.debug(
            "[feedback] Feedback history retrieved",
            extra={"itemId": item_id, "count": len(entries)},
        )

        return [
            FeedbackHistoryEntry(
                id=str(entry["_id"]),
                itemId=entry["item_id"],
                itemType=entry["item_type"],
                feedback=entry["feedback"],
                timestamp=entry["created_at"].isoformat(),
                status=entry.get("status", "submitted"),
                regeneratedAt=entry.get("regenerated_at").isoformat()
                if entry.get("regenerated_at")
                else None,
                version=entry.get("version", 0),
            )
            for entry in entries
        ]

    except Exception as exc:
        logger.error(
            "[feedback] Error getting feedback history",
            exc_info=True,
            extra={"itemId": item_id, "itemType": itemType},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve feedback history: {str(exc)}",
        ) from exc


@router.get("/regeneration-count/{item_id}", response_model=RegenerationCountResponse)
async def get_regeneration_count(
    item_id: str, itemType: str = Query(..., description="Type of item: 'feature', 'story', or 'visualization'")
) -> RegenerationCountResponse:
    """Get regeneration count for an item."""
    logger.debug(
        "[feedback] Getting regeneration count",
        extra={"itemId": item_id, "itemType": itemType},
    )

    try:
        db = get_database()
        count = await _get_regeneration_count(db, item_id, itemType)

        logger.debug(
            "[feedback] Regeneration count retrieved",
            extra={"itemId": item_id, "count": count},
        )

        return RegenerationCountResponse(count=count)

    except Exception as exc:
        logger.error(
            "[feedback] Error getting regeneration count",
            exc_info=True,
            extra={"itemId": item_id, "itemType": itemType},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve regeneration count: {str(exc)}",
        ) from exc


async def _get_regeneration_count(
    db, item_id: str, item_type: str
) -> int:
    """Helper function to get regeneration count for an item."""
    count = await db["feedback_history"].count_documents(
        {
            "item_id": item_id,
            "item_type": item_type,
            "status": "regenerated",
        }
    )
    return count


# ========================================
# Chatbot Endpoints
# ========================================

@router.post("/chatbot/message", response_model=ChatbotResponse)
async def send_chatbot_message(request: ChatbotRequest) -> ChatbotResponse:
    """Send a message to the feedback chatbot and get AI response."""
    logger.debug(
        "[feedback-chatbot] Sending message to chatbot",
        extra={
            "messageLength": len(request.message),
            "conversationId": request.conversationId,
            "hasContext": bool(request.context),
        },
    )

    try:
        db = get_database()
        
        # Generate or use existing conversation ID
        conversation_id = request.conversationId or str(uuid.uuid4())
        
        # Get existing conversation history if available
        chat_history = []
        if request.conversationId:
            conversation = await db["chatbot_conversations"].find_one(
                {"_id": conversation_id}
            )
            if conversation:
                chat_history = conversation.get("messages", [])
                logger.debug(
                    f"[feedback-chatbot] Found existing conversation | messages={len(chat_history)}"
                )
        
        # Build context from request
        context = request.context or {}
        if request.itemType:
            context["itemType"] = request.itemType
        if request.itemId:
            context["itemId"] = request.itemId
        if request.projectId:
            context["projectId"] = request.projectId
        
        logger.debug(
            "[feedback-chatbot] Calling chatbot service",
            extra={
                "conversationId": conversation_id,
                "historyLength": len(chat_history),
            },
        )
        
        # Generate AI response
        response = await chatbot_service.generate_response(
            user_message=request.message,
            chat_history=chat_history,
            context=context,
        )
        
        # Save conversation to database
        timestamp = datetime.utcnow()
        
        # Add user message to history
        chat_history.append({
            "role": "user",
            "content": request.message,
            "timestamp": timestamp.isoformat(),
        })
        
        # Add assistant response to history
        chat_history.append({
            "role": "assistant",
            "content": response["response"],
            "timestamp": response["timestamp"],
        })
        
        # Update or create conversation
        await db["chatbot_conversations"].update_one(
            {"_id": conversation_id},
            {
                "$set": {
                    "messages": chat_history,
                    "updated_at": timestamp,
                    "project_id": request.projectId,
                    "item_id": request.itemId,
                    "item_type": request.itemType,
                },
                "$setOnInsert": {
                    "created_at": timestamp,
                },
            },
            upsert=True,
        )
        
        logger.info(
            "[feedback-chatbot] Message sent and response generated",
            extra={
                "conversationId": conversation_id,
                "messageId": response["message_id"],
                "totalMessages": len(chat_history),
            },
        )
        
        return ChatbotResponse(
            conversationId=conversation_id,
            messageId=response["message_id"],
            response=response["response"],
            timestamp=response["timestamp"],
            metadata=response.get("metadata"),
        )
    
    except Exception as exc:
        logger.error(
            "[feedback-chatbot] Error processing chatbot message",
            exc_info=True,
            extra={"conversationId": request.conversationId},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chatbot message: {str(exc)}",
        ) from exc


@router.post("/chatbot/suggest-improvements", response_model=FeedbackSuggestionResponse)
async def suggest_feedback_improvements(
    request: FeedbackSuggestionRequest,
) -> FeedbackSuggestionResponse:
    """Get AI suggestions to improve user feedback."""
    logger.debug(
        "[feedback-chatbot] Suggesting feedback improvements",
        extra={
            "feedbackLength": len(request.feedback),
            "itemType": request.itemType,
        },
    )

    try:
        result = await chatbot_service.suggest_feedback_improvements(
            original_feedback=request.feedback,
            item_type=request.itemType,
            item_content=request.itemContent,
        )
        
        logger.info(
            "[feedback-chatbot] Suggestions generated",
            extra={"messageId": result["message_id"], "itemType": request.itemType},
        )
        
        return FeedbackSuggestionResponse(
            suggestions=result["suggestions"],
            originalFeedback=result["original_feedback"],
            itemType=result["item_type"],
            messageId=result["message_id"],
        )
    
    except Exception as exc:
        logger.error(
            "[feedback-chatbot] Error suggesting improvements",
            exc_info=True,
            extra={"itemType": request.itemType},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(exc)}",
        ) from exc


@router.post("/chatbot/explain-regeneration", response_model=RegenerationExplanationResponse)
async def explain_regeneration(
    request: RegenerationExplanationRequest,
) -> RegenerationExplanationResponse:
    """Get AI explanation of what changed in a regeneration and why."""
    logger.debug(
        "[feedback-chatbot] Explaining regeneration",
        extra={"itemType": request.itemType},
    )

    try:
        explanation = await chatbot_service.explain_regeneration(
            item_type=request.itemType,
            original_content=request.originalContent,
            regenerated_content=request.regeneratedContent,
            feedback=request.feedback,
        )
        
        logger.info(
            "[feedback-chatbot] Explanation generated",
            extra={"itemType": request.itemType},
        )
        
        return RegenerationExplanationResponse(
            explanation=explanation,
            itemType=request.itemType,
        )
    
    except Exception as exc:
        logger.error(
            "[feedback-chatbot] Error generating explanation",
            exc_info=True,
            extra={"itemType": request.itemType},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(exc)}",
        ) from exc


@router.get("/chatbot/conversation/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(conversation_id: str) -> ConversationHistoryResponse:
    """Get the full history of a chatbot conversation."""
    logger.debug(
        "[feedback-chatbot] Getting conversation history",
        extra={"conversationId": conversation_id},
    )

    try:
        db = get_database()
        
        conversation = await db["chatbot_conversations"].find_one(
            {"_id": conversation_id}
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {conversation_id}",
            )
        
        messages = [
            ChatMessage(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                timestamp=msg.get("timestamp"),
            )
            for msg in conversation.get("messages", [])
        ]
        
        logger.info(
            "[feedback-chatbot] Conversation history retrieved",
            extra={"conversationId": conversation_id, "messageCount": len(messages)},
        )
        
        return ConversationHistoryResponse(
            conversationId=conversation_id,
            messages=messages,
            createdAt=conversation.get("created_at").isoformat()
            if conversation.get("created_at")
            else datetime.utcnow().isoformat(),
            updatedAt=conversation.get("updated_at").isoformat()
            if conversation.get("updated_at")
            else datetime.utcnow().isoformat(),
        )
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "[feedback-chatbot] Error getting conversation history",
            exc_info=True,
            extra={"conversationId": conversation_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(exc)}",
        ) from exc


@router.delete("/chatbot/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict:
    """Delete a chatbot conversation."""
    logger.debug(
        "[feedback-chatbot] Deleting conversation",
        extra={"conversationId": conversation_id},
    )

    try:
        db = get_database()
        
        result = await db["chatbot_conversations"].delete_one(
            {"_id": conversation_id}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {conversation_id}",
            )
        
        logger.info(
            "[feedback-chatbot] Conversation deleted",
            extra={"conversationId": conversation_id},
        )
        
        return {
            "message": "Conversation deleted successfully",
            "conversationId": conversation_id,
        }
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "[feedback-chatbot] Error deleting conversation",
            exc_info=True,
            extra={"conversationId": conversation_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(exc)}",
        ) from exc

