from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import List
from textwrap import dedent

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from .schemas import (
    Conversation,
    ConversationCreate,
    FeedbackRequest,
    LoginRequest,
    LoginResponse,
    Message,
    MessageCreate,
    User,
)
from .storage import storage

load_dotenv()

logger = logging.getLogger("agent1")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    logger.warning("ANTHROPIC_API_KEY environment variable is not set. Responses will fall back to template text.")

chat_model: ChatAnthropic | None = None
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", dedent("""
You are Agent-1, a product requirements assistant. For every customer prompt you receive, produce a clear, structured list of software features that would satisfy the request. Do not write code. Focus on high-level capabilities, user flows, integrations, data requirements, and success metrics. Number the features, and group related items when appropriate. Keep the tone professional and concise.
""").strip()),
        ("human", "Customer request:\n{user_message}\n\nProvide the feature list."),
    ]
)

app = FastAPI(
    title="Angular Chat Backend",
    description="FastAPI backend that powers the Agent-1 feature generator",
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_chat_model() -> ChatAnthropic | None:
    global chat_model
    if chat_model is None and ANTHROPIC_API_KEY:
        chat_model = ChatAnthropic(
            model=ANTHROPIC_MODEL,
            temperature=0.2,
            anthropic_api_key=ANTHROPIC_API_KEY,
        )
    return chat_model


@app.get("/api/health", response_model=dict)
def health_check() -> dict:
    logger.debug("Health check requested")
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    logger.debug("Login attempt for %s", payload.email)
    user = User(email=payload.email, name=payload.email.split("@")[0])
    return LoginResponse(user=user)


@app.get("/api/conversations", response_model=List[Conversation])
def get_conversations() -> List[Conversation]:
    logger.debug("Fetching conversations")
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation, status_code=201)
def create_conversation(payload: ConversationCreate | None = None) -> Conversation:
    logger.info("Creating new conversation title=%s", payload.title if payload else None)
    return storage.create_conversation(title=payload.title if payload else None)


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
def get_conversation(conversation_id: str) -> Conversation:
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        logger.warning("Conversation %s not found", conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/messages", response_model=Conversation)
def send_message(conversation_id: str, payload: MessageCreate) -> Conversation:
    logger.info("[Agent1] conversation=%s prompt=%s", conversation_id, payload.content)
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        logger.warning("Conversation %s not found", conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = datetime.now(timezone.utc)
    user_message = Message(
        id=storage.generate_id(),
        content=payload.content.strip(),
        role="user",
        timestamp=now,
    )
    conversation = storage.add_message(conversation_id, user_message)

    try:
        assistant_response = _generate_features(payload.content)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Feature generation failed: %s", exc)
        assistant_response = (
            "I'm sorry, I couldn't reach the feature generation service. "
            "Please try again in a moment or adjust your prompt."
        )

    assistant_message = Message(
        id=storage.generate_id(),
        content=assistant_response,
        role="assistant",
        timestamp=datetime.now(timezone.utc),
    )

    conversation = storage.add_message(conversation_id, assistant_message)
    logger.info("[Agent1] conversation=%s generated features message=%s", conversation_id, assistant_message.id)
    return conversation


@app.post(
    "/api/conversations/{conversation_id}/messages/{message_id}/feedback",
    response_model=Conversation,
)
def set_feedback(conversation_id: str, message_id: str, payload: FeedbackRequest) -> Conversation:
    logger.info(
        "[Agent1] feedback conversation=%s message=%s feedback=%s",
        conversation_id,
        message_id,
        payload.feedback,
    )
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        logger.warning("Conversation %s not found for feedback", conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        storage.update_message_feedback(conversation_id, message_id, payload.feedback)
    except ValueError as exc:
        logger.warning("Feedback error: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    updated_conversation = storage.get_conversation(conversation_id)
    if updated_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return updated_conversation


@app.delete("/api/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str) -> None:
    logger.info("Deleting conversation %s", conversation_id)
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        logger.warning("Conversation %s not found", conversation_id)
        raise HTTPException(status_code=404, detail="Conversation not found")
    storage.delete_conversation(conversation_id)


@app.delete("/api/conversations", response_model=Conversation)
def clear_conversations() -> Conversation:
    logger.info("Clearing all conversations")
    return storage.clear_conversations()


def _generate_features(user_message: str) -> str:
    model = _get_chat_model()
    if model is None:
        logger.warning("Anthropic API key missing; using fallback responder")
        return _fallback_response(user_message)

    messages = prompt_template.format_messages(user_message=user_message.strip())
    logger.debug("Invoking Claude with %d prompt messages", len(messages))
    ai_message = model.invoke(messages)
    logger.debug("Claude response length=%d", len(ai_message.content or ""))
    return ai_message.content.strip()


def _fallback_response(user_message: str) -> str:
    snippet = user_message.strip()[:80]
    if len(snippet) < len(user_message):
        snippet += "..."
    return (
        "I captured the following customer requirement and would normally request features from Claude: "
        f"\n\n> {snippet}\n\n"
        "Please configure the Anthropic API key to receive generated feature plans."
    )
