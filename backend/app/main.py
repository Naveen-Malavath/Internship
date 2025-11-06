from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    Conversation,
    ConversationCreate,
    LoginRequest,
    LoginResponse,
    Message,
    MessageCreate,
    User,
)
from .storage import storage

app = FastAPI(
    title="Angular Chat Backend",
    description="Simple FastAPI backend that powers the Angular chat interface",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=dict)
def health_check() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    # NOTE: For demo purposes we simply echo the email address back.
    # In a production application you must verify credentials securely.
    user = User(email=payload.email, name=payload.email.split("@")[0])
    return LoginResponse(user=user)


@app.get("/api/conversations", response_model=List[Conversation])
def get_conversations() -> List[Conversation]:
    return storage.list_conversations()


@app.post("/api/conversations", response_model=Conversation, status_code=201)
def create_conversation(payload: ConversationCreate | None = None) -> Conversation:
    return storage.create_conversation(title=payload.title if payload else None)


@app.get("/api/conversations/{conversation_id}", response_model=Conversation)
def get_conversation(conversation_id: str) -> Conversation:
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.post("/api/conversations/{conversation_id}/messages", response_model=Conversation)
def send_message(conversation_id: str, payload: MessageCreate) -> Conversation:
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    now = datetime.now(timezone.utc)
    user_message = Message(
        id=storage.generate_id(),
        content=payload.content,
        role="user",
        timestamp=now,
    )

    conversation = storage.add_message(conversation_id, user_message)

    assistant_response = _generate_response(payload.content)
    assistant_message = Message(
        id=storage.generate_id(),
        content=assistant_response,
        role="assistant",
        timestamp=datetime.now(timezone.utc),
    )

    conversation = storage.add_message(conversation_id, assistant_message)
    return conversation


@app.delete("/api/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str) -> None:
    conversation = storage.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    storage.delete_conversation(conversation_id)


@app.delete("/api/conversations", response_model=Conversation)
def clear_conversations() -> Conversation:
    return storage.clear_conversations()


def _generate_response(user_message: str) -> str:
    templates = [
        "I see you're curious about \"{snippet}\". This backend demo stores and responds to chat history without hitting an external AI service.",
        "Thanks for the prompt! In a production system I would forward \"{snippet}\" to an AI provider and stream the response back to the UI.",
        "The message \"{snippet}\" has been recorded. This FastAPI backend is ready for you to plug in your own AI integration.",
        "Interesting! Your prompt \"{snippet}\" demonstrates how the Angular frontend communicates with this FastAPI backend.",
    ]
    snippet = user_message.strip()[:50]
    if len(snippet) < len(user_message):
        snippet += "..."
    index = hash(user_message) % len(templates)
    return templates[index].format(snippet=snippet)
