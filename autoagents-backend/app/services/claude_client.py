"""Shared Claude client helpers."""

from __future__ import annotations

import json
import os
from typing import Optional

from anthropic import AsyncAnthropic
from anthropic.types import Message

DEFAULT_CLAUDE_MODEL = "claude-3-5-haiku-20241022"

_client: Optional[AsyncAnthropic] = None


def get_claude_client() -> AsyncAnthropic:
    """Return a singleton AsyncAnthropic client."""
    global _client
    if _client is None:
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise RuntimeError("CLAUDE_API_KEY is not configured.")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


def extract_text(message: Message) -> str:
    """Extract the first text block from a Claude message."""
    for block in message.content:
        if block.type == "text":
            return block.text
    raise RuntimeError("Claude response did not contain a text block.")


def coerce_json(payload: str) -> dict:
    """Parse JSON payload from Claude, raising a helpful error on failure."""
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Claude returned invalid JSON: {payload}") from exc
