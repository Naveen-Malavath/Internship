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
)
from ..services.feedback_service import FeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

# Initialize feedback service
feedback_service = FeedbackService()


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

        logger.info(
            "[feedback] Feedback submitted successfully",
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

