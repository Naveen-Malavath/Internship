"""Agent-1 service responsible for feature generation."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import List

from anthropic import APIError
from bson import ObjectId
from fastapi import HTTPException, status

from .claude_client import (
    DEFAULT_CLAUDE_MODEL,
    coerce_json,
    extract_text,
    get_claude_client,
)

logger = logging.getLogger(__name__)


class Agent1Service:
    """Service wrapper for generating features via Claude."""

    def __init__(self, model: str | None = None) -> None:
        # Priority: explicit model > CLAUDE_MODEL_DEBUG > CLAUDE_MODEL > default
        debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
        if model is None and debug_model:
            self.model = debug_model
            logger.info(f"[agent1] Using DEBUG model from CLAUDE_MODEL_DEBUG: {self.model}")
        else:
            self.model = model or os.getenv("CLAUDE_MODEL", DEFAULT_CLAUDE_MODEL)
            logger.info(f"[agent1] Initialized with Claude Sonnet 4.5 model: {self.model}")

    async def generate_features(self, project_title: str, project_prompt: str) -> List[str]:
        """Generate feature descriptions for the given project using Claude."""
        logger.info(f"[agent1] Starting feature generation with Claude Sonnet 4.5 | model={self.model} | title={project_title[:50]}")
        
        # Check for mock mode (for development when credits are low)
        mock_mode = os.getenv("AGENT_MOCK_MODE", "").lower() in ("true", "1", "yes")
        if mock_mode:
            logger.warning("[agent1] MOCK MODE ENABLED - Returning mock features without API call")
            return self._generate_mock_features(project_title, project_prompt)
        
        try:
            client = get_claude_client()
            logger.debug("[agent1] Claude client obtained successfully")
        except RuntimeError as exc:
            logger.error(f"[agent1] Failed to get Claude client: {exc}", exc_info=True)
            raise

        system_prompt = (
            "You are Agent-1, a product strategist translating user ideas into actionable features. "
            "Respond ONLY with valid JSON:\n"
            "{\n"
            '  "features": [\n'
            '    {"title": "Feature name", "description": "2-3 sentences", "acceptanceCriteria": ["Criterion 1", "Criterion 2"]}\n'
            "  ]\n"
            "}\n"
            "Provide 8-12 concise, implementation-ready features directly addressing the user's prompt."
        )
        user_prompt = (
            f"Project: {project_title or 'Untitled'}\n"
            f"User Prompt: {project_prompt or 'No prompt provided.'}\n\n"
            "Generate 8-12 features that directly address the prompt. "
            "Focus on core functionality, user experience, and implementation feasibility. "
            "Return JSON now."
        )

        try:
            # Increased max_tokens to prevent truncation of JSON responses with 8-12 features
            max_tokens = 4000
            logger.info(f"[agent1] Attempting API call | model={self.model} | max_tokens={max_tokens} | temperature=0.4")
            logger.debug(f"[agent1] System prompt length: {len(system_prompt)} chars")
            logger.debug(f"[agent1] User prompt length: {len(user_prompt)} chars")
            logger.debug(f"[agent1] User prompt preview: {user_prompt[:200]}...")
            
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.4,  # Lower temperature for faster, more focused responses
                system=system_prompt,
                messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
            )
            usage = getattr(response, "usage", None)
            if usage:
                logger.info(f"[agent1] API call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
            else:
                logger.info("[agent1] API call successful")
        except APIError as exc:  # pragma: no cover - upstream error surface
            # Extract error message - try multiple methods to ensure we catch it
            error_message = str(exc)
            # Also check if the exception has a message attribute or body
            if hasattr(exc, 'message') and exc.message:
                error_message = exc.message
            elif hasattr(exc, 'body') and isinstance(exc.body, dict):
                error_dict = exc.body.get('error', {}) if isinstance(exc.body.get('error'), dict) else {}
                if error_dict.get('message'):
                    error_message = error_dict['message']
                elif exc.body.get('message'):
                    error_message = exc.body['message']
            
            error_type = getattr(exc, 'type', 'unknown')
            error_status = getattr(exc, 'status_code', None)
            
            # Enhanced debug logging
            logger.error(f"[agent1] APIError encountered")
            logger.error(f"[agent1] Error Type: {error_type}")
            logger.error(f"[agent1] Error Status: {error_status}")
            logger.error(f"[agent1] Error Message: {error_message}")
            if hasattr(exc, 'body'):
                logger.debug(f"[agent1] Error body: {exc.body}")
            logger.debug(f"[agent1] Full exception object: {exc}")
            logger.debug(f"[agent1] Exception attributes: {dir(exc)}")
            
            # Check for specific error types
            error_message_lower = error_message.lower()
            
            # Check for low credit balance error
            if "credit balance" in error_message_lower or "too low" in error_message_lower or "purchase credits" in error_message_lower:
                user_friendly_message = (
                    "Anthropic API credit balance is too low. "
                    "Please add credits to your Anthropic account at https://console.anthropic.com/settings/billing "
                    "to continue using Agent-1."
                )
                logger.error(f"[agent1] CREDIT BALANCE ERROR: {user_friendly_message}")
                logger.error(f"[agent1] Original error: {error_message}")
                raise RuntimeError(user_friendly_message) from exc
            
            # Check for authentication errors
            if "authentication" in error_message_lower or "api key" in error_message_lower or error_status == 401:
                user_friendly_message = (
                    "Anthropic API authentication failed. "
                    "Please check your ANTHROPIC_API_KEY environment variable."
                )
                logger.error(f"[agent1] AUTHENTICATION ERROR: {user_friendly_message}")
                logger.error(f"[agent1] Original error: {error_message}")
                raise RuntimeError(user_friendly_message) from exc
            
            # Check for rate limiting
            if "rate limit" in error_message_lower or "too many requests" in error_message_lower or error_status == 429:
                user_friendly_message = (
                    "Anthropic API rate limit exceeded. "
                    "Please wait a moment and try again."
                )
                logger.error(f"[agent1] RATE LIMIT ERROR: {user_friendly_message}")
                logger.error(f"[agent1] Original error: {error_message}")
                raise RuntimeError(user_friendly_message) from exc
            
            # If model not found, try fallback to Claude 3.5 Sonnet (proven to work)
            if "not_found_error" in error_message_lower or error_status == 404 or "model not found" in error_message_lower:
                fallback_model = "claude-3-5-sonnet-latest"
                logger.warning(f"[agent1] Model {self.model} not found, trying fallback: {fallback_model}")
                logger.debug(f"[agent1] Attempting fallback API call with {fallback_model}")
                try:
                    response = await client.messages.create(
                        model=fallback_model,
                        max_tokens=4000,
                        temperature=0.4,
                        system=system_prompt,
                        messages=[{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
                    )
                    usage = getattr(response, "usage", None)
                    if usage:
                        logger.info(f"[agent1] Fallback model ({fallback_model}) call successful | input_tokens={usage.input_tokens} | output_tokens={usage.output_tokens}")
                    else:
                        logger.info(f"[agent1] Fallback model ({fallback_model}) call successful")
                except APIError as fallback_exc:
                    fallback_error_message = str(fallback_exc)
                    logger.error(f"[agent1] Fallback model also failed: {fallback_exc}", exc_info=True)
                    logger.error(f"[agent1] Fallback error message: {fallback_error_message}")
                    
                    # Check if fallback also has credit balance error
                    if "credit balance" in fallback_error_message.lower() or "too low" in fallback_error_message.lower():
                        user_friendly_message = (
                            "Anthropic API credit balance is too low. "
                            "Please add credits to your Anthropic account at https://console.anthropic.com/settings/billing "
                            "to continue using Agent-1."
                        )
                        logger.error(f"[agent1] CREDIT BALANCE ERROR (fallback): {user_friendly_message}")
                        raise RuntimeError(user_friendly_message) from fallback_exc
                    
                    raise RuntimeError(f"Agent-1 failed with both {self.model} and fallback {fallback_model}: {fallback_exc}") from fallback_exc
            else:
                # Generic error handling
                logger.error(f"[agent1] API call failed with unhandled error type")
                logger.error(f"[agent1] Error details - Type: {error_type}, Status: {error_status}, Message: {error_message}")
                logger.debug(f"[agent1] Full exception traceback:", exc_info=True)
                raise RuntimeError(f"Agent-1 failed to generate features: {error_message} (Type: {error_type}, Status: {error_status})") from exc

        logger.debug("[agent1] Extracting and parsing response")
        response_text = extract_text(response)
        payload = coerce_json(response_text)
        features = payload.get("features", [])
        if not isinstance(features, list):
            logger.error(f"[agent1] Unexpected payload structure: {type(features)}")
            raise RuntimeError("Agent-1 returned an unexpected payload.")

        # Handle both formats: objects with title/description/acceptanceCriteria OR simple strings
        filtered_features = []
        for feature in features:
            if isinstance(feature, str) and feature.strip():
                # Simple string format
                filtered_features.append(feature.strip())
            elif isinstance(feature, dict):
                # Object format - extract title and description
                title = feature.get("title", "").strip()
                description = feature.get("description", "").strip()
                if title:
                    # Combine title and description for backward compatibility
                    if description:
                        feature_text = f"{title}: {description}"
                    else:
                        feature_text = title
                    filtered_features.append(feature_text)
                elif description:
                    # Fallback to description if no title
                    filtered_features.append(description)
            # Skip invalid entries
        
        if not filtered_features:
            logger.warning(f"[agent1] No valid features extracted from response. Payload structure: {type(features[0]) if features else 'empty'}")
            # Try to extract at least some text from the response
            if features:
                logger.warning(f"[agent1] Features list structure: {features[:2]}")
        
        logger.info(f"[agent1] Feature generation complete | generated={len(filtered_features)} features")
        return filtered_features

    def _generate_mock_features(self, project_title: str, project_prompt: str) -> List[str]:
        """Generate mock features for development/testing when API credits are unavailable."""
        logger.debug("[agent1] Generating mock features based on prompt")
        
        # Extract keywords from prompt to make mock features relevant
        prompt_lower = (project_prompt or "").lower()
        
        # Base mock features
        mock_features = [
            "User Authentication and Authorization",
            "Dashboard and Analytics",
            "Data Management and Storage",
            "API Integration and External Services",
            "Notification System",
            "Search and Filtering",
            "Reporting and Export",
            "Settings and Configuration",
        ]
        
        # Customize based on prompt keywords
        if any(word in prompt_lower for word in ["e-commerce", "shopping", "store", "cart"]):
            mock_features = [
                "Product Catalog Management",
                "Shopping Cart Functionality",
                "Checkout and Payment Processing",
                "Order Management System",
                "Inventory Tracking",
                "Customer Reviews and Ratings",
                "Shipping and Delivery Tracking",
                "User Account Management",
            ]
        elif any(word in prompt_lower for word in ["healthcare", "medical", "patient", "hospital"]):
            mock_features = [
                "Patient Registration and Management",
                "Appointment Scheduling System",
                "Medical Records Management",
                "Prescription Management",
                "Billing and Insurance Processing",
                "Doctor Dashboard",
                "Lab Results Integration",
                "Telemedicine Capabilities",
            ]
        elif any(word in prompt_lower for word in ["banking", "finance", "payment", "transaction"]):
            mock_features = [
                "Account Management",
                "Transaction Processing",
                "Payment Transfer System",
                "Loan Application Processing",
                "Investment Portfolio Tracking",
                "Credit Card Management",
                "Fraud Detection System",
                "Financial Reporting",
            ]
        elif any(word in prompt_lower for word in ["education", "learning", "course", "student"]):
            mock_features = [
                "Course Management System",
                "Student Enrollment",
                "Assignment Submission Portal",
                "Grading and Assessment",
                "Video Lecture Platform",
                "Discussion Forums",
                "Progress Tracking",
                "Certificate Generation",
            ]
        
        logger.info(f"[agent1] Mock mode: Generated {len(mock_features)} mock features")
        return mock_features


async def generate_features_for_project(project_id: str, db) -> List[dict]:
    """Generate and persist features for a project using Claude."""
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project ID.")

    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    service = Agent1Service()
    try:
        feature_texts = await service.generate_features(
            project_title=project.get("title", ""),
            project_prompt=project.get("prompt", ""),
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    now = datetime.utcnow()
    documents = [
        {
            "project_id": project_id,
            "feature_text": text.strip(),
            "order_index": index,
            "created_at": now,
        }
        for index, text in enumerate(feature_texts, start=1)
    ]

    if not documents:
        return []

    result = await db["features"].insert_many(documents)
    inserted = []
    for document, inserted_id in zip(documents, result.inserted_ids, strict=False):
        document["_id"] = str(inserted_id)
        inserted.append(document)

    return inserted
