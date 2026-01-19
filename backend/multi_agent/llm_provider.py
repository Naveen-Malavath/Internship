"""LLM Provider - Unified interface for Claude/Anthropic"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from anthropic import Anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolCall(BaseModel):
    """Tool/function call from LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]


class LLMResponse(BaseModel):
    """Response from LLM"""
    content: str
    tool_calls: List[ToolCall] = []
    finish_reason: str
    usage: Dict[str, int] = {}


class LLMProvider:
    """
    Unified interface for Anthropic Claude
    Supports function/tool calling
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize LLM provider with Anthropic Claude"""
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.client = Anthropic(api_key=api_key)
        logger.info(f"[LLM] Initialized Anthropic provider with model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 16384,  # FIXED: Increased from 4096 for production-quality code
    ) -> LLMResponse:
        """
        Send chat request to Claude with optional tool calling
        """
        logger.info(f"[LLM] Chat request: {len(messages)} messages, {len(tools) if tools else 0} tools")

        # Separate system message
        system_message = ""
        chat_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append({"role": msg["role"], "content": msg["content"]})

        kwargs = {
            "model": self.model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if system_message:
            kwargs["system"] = system_message

        if tools:
            # Convert OpenAI tool format to Anthropic format
            anthropic_tools = []
            for tool in tools:
                if "function" in tool:
                    anthropic_tools.append({
                        "name": tool["function"]["name"],
                        "description": tool["function"]["description"],
                        "input_schema": tool["function"]["parameters"],
                    })
            kwargs["tools"] = anthropic_tools

        try:
            response = self.client.messages.create(**kwargs)

            # Extract content and tool calls
            content = ""
            tool_calls = []

            for block in response.content:
                if hasattr(block, 'type'):
                    if block.type == "text":
                        content += getattr(block, 'text', '')
                    elif block.type == "tool_use":
                        tool_calls.append(ToolCall(
                            id=block.id,
                            name=block.name,
                            arguments=block.input
                        ))
                elif isinstance(block, str):
                    content += block

            logger.info(f"[LLM] Response: {len(content)} chars, {len(tool_calls)} tool calls")

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=response.stop_reason or "end_turn",
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            )

        except Exception as e:
            logger.error(f"[LLM] API error: {e}")
            raise
