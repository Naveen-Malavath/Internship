"""LLM Provider abstraction layer supporting multiple AI models"""

import json
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from anthropic import Anthropic
from loguru import logger
from openai import OpenAI
from pydantic import BaseModel

from .config import get_config


class Provider(str, Enum):
    """Supported LLM providers"""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class Message(BaseModel):
    """Chat message"""

    role: str  # 'system', 'user', 'assistant', 'tool'
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


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
    Unified interface for multiple LLM providers
    Supports OpenAI and Anthropic with function/tool calling
    """

    def __init__(
        self,
        provider: Optional[Provider] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize LLM provider
        
        Args:
            provider: LLM provider (openai or anthropic)
            model: Model name
            api_key: API key (if not in config)
        """
        config = get_config()

        # Determine provider
        if provider is None:
            provider = Provider(config.default_llm_provider)
        self.provider = provider

        # Setup provider-specific client
        if self.provider == Provider.OPENAI:
            self.model = model or config.openai_model
            api_key = api_key or config.openai_api_key
            if not api_key:
                raise ValueError("OpenAI API key not found in config or environment")
            self.client = OpenAI(api_key=api_key)
            logger.info(f"Initialized OpenAI provider with model: {self.model}")

        elif self.provider == Provider.ANTHROPIC:
            self.model = model or config.anthropic_model
            api_key = api_key or config.anthropic_api_key
            if not api_key:
                raise ValueError(
                    "Anthropic API key not found in config or environment"
                )
            self.client = Anthropic(api_key=api_key)
            logger.info(f"Initialized Anthropic provider with model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 16384,  # FIXED: Increased from 4096 for production-quality code
    ) -> LLMResponse:
        """
        Send chat request to LLM with optional tool calling
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool/function definitions
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            LLMResponse with content and tool calls
        """
        logger.info(f"📞 [LLM] chat() called. Provider: {self.provider}, messages: {len(messages)}, tools: {len(tools) if tools else 0}")
        print(f"📞 [LLM] chat() called. Provider: {self.provider}")
        
        try:
            if self.provider == Provider.OPENAI:
                logger.info(f"📞 [LLM] Routing to OpenAI")
                print(f"📞 [LLM] Routing to OpenAI")
                return self._chat_openai(messages, tools, temperature, max_tokens)
            elif self.provider == Provider.ANTHROPIC:
                logger.info(f"📞 [LLM] Routing to Anthropic")
                print(f"📞 [LLM] Routing to Anthropic")
                return self._chat_anthropic(messages, tools, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown provider: {self.provider}")
        except Exception as e:
            logger.error(f"🔴 [LLM] Error in chat(): {e}", exc_info=True)
            print(f"🔴 [LLM] Error in chat(): {e}")
            import traceback
            traceback.print_exc()
            raise

    def _chat_openai(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """OpenAI chat completion"""
        logger.info(f"🔵 [OPENAI] Calling API with model={self.model}")
        print(f"🔵 [OPENAI] Calling API with model={self.model}")
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**kwargs)
            logger.info(f"🔵 [OPENAI] API response received. Type: {type(response)}")
            print(f"🔵 [OPENAI] API response received. Type: {type(response)}")
            
            choice = response.choices[0]
            logger.info(f"🔵 [OPENAI] Choice type: {type(choice)}")
            print(f"🔵 [OPENAI] Choice type: {type(choice)}")

            # Extract tool calls if present
            tool_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls.append(
                        ToolCall(
                            id=tc.id,
                            name=tc.function.name,
                            arguments=json.loads(tc.function.arguments),
                        )
                    )

            return LLMResponse(
                content=choice.message.content or "",
                tool_calls=tool_calls,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            )

        except Exception as e:
            logger.error(f"🔴 [OPENAI] API error: {e}", exc_info=True)
            print(f"🔴 [OPENAI] API error: {e}")
            import traceback
            traceback.print_exc()
            raise

    def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Anthropic chat completion"""
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
                    anthropic_tools.append(
                        {
                            "name": tool["function"]["name"],
                            "description": tool["function"]["description"],
                            "input_schema": tool["function"]["parameters"],
                        }
                    )
            kwargs["tools"] = anthropic_tools

        try:
            logger.info(f"🔵 [ANTHROPIC] Calling API with model={self.model}, messages={len(chat_messages)}, tools={len(anthropic_tools) if tools else 0}")
            print(f"🔵 [ANTHROPIC] Calling API with model={self.model}")
            
            response = self.client.messages.create(**kwargs)

            # Extract content and tool calls
            content = ""
            tool_calls = []

            # Log response structure for debugging
            logger.info(f"🔵 [ANTHROPIC] API response received. Type: {type(response)}")
            print(f"🔵 [ANTHROPIC] API response received. Type: {type(response)}")
            
            logger.debug(f"Anthropic API response type: {type(response)}")
            logger.debug(f"Response content type: {type(response.content) if hasattr(response, 'content') else 'N/A'}")
            
            if hasattr(response, 'content'):
                logger.info(f"🔵 [ANTHROPIC] response.content type: {type(response.content)}")
                print(f"🔵 [ANTHROPIC] response.content type: {type(response.content)}")
                logger.info(f"🔵 [ANTHROPIC] response.content value: {repr(response.content)[:200]}")
                print(f"🔵 [ANTHROPIC] response.content value (first 200 chars): {repr(response.content)[:200]}")
            else:
                logger.error("🔴 [ANTHROPIC] response has no 'content' attribute")
                print("🔴 [ANTHROPIC] response has no 'content' attribute")
            
            # Ensure response.content exists and is iterable
            if not hasattr(response, 'content'):
                logger.error("Anthropic API response missing 'content' attribute")
                raise ValueError("API response missing 'content' attribute")
            
            if response.content is None:
                logger.error("Anthropic API response content is None")
                raise ValueError("API response content is None")
            
            # Handle case where response.content might be a string (error response)
            if isinstance(response.content, str):
                logger.error(f"Anthropic API returned string content instead of blocks: {response.content}")
                raise ValueError(f"Unexpected API response format: received string instead of list: {response.content}")
            
            # Ensure response.content is iterable (list, tuple, etc.)
            try:
                logger.info(f"🟡 [ANTHROPIC] Attempting to iterate over response.content")
                print(f"🟡 [ANTHROPIC] Attempting to iterate over response.content")
                logger.info(f"🟡 [ANTHROPIC] response.content type before iter(): {type(response.content)}")
                print(f"🟡 [ANTHROPIC] response.content type before iter(): {type(response.content)}")
                
                # Check if it's already a list or similar
                if isinstance(response.content, (list, tuple)):
                    logger.info(f"🟡 [ANTHROPIC] response.content is a {type(response.content).__name__} with {len(response.content)} items")
                    print(f"🟡 [ANTHROPIC] response.content is a {type(response.content).__name__} with {len(response.content)} items")
                
                content_iter = iter(response.content)
                logger.info(f"✅ [ANTHROPIC] Successfully created iterator")
                print(f"✅ [ANTHROPIC] Successfully created iterator")
            except TypeError as e:
                logger.error(f"🔴 [ANTHROPIC] ERROR creating iterator: {e}")
                print(f"🔴 [ANTHROPIC] ERROR creating iterator: {e}")
                logger.error(f"Anthropic API response content is not iterable: {type(response.content)}")
                raise ValueError(f"API response content is not iterable: {type(response.content)}")
            
            block_count = 0
            logger.info(f"🟢 [ANTHROPIC] Starting to iterate over blocks")
            print(f"🟢 [ANTHROPIC] Starting to iterate over blocks")
            
            for block in content_iter:
                block_count += 1
                # Log block type for debugging
                logger.info(f"🟢 [ANTHROPIC] Processing block #{block_count}. Block type: {type(block)}")
                print(f"🟢 [ANTHROPIC] Processing block #{block_count}. Block type: {type(block)}")
                logger.info(f"🟢 [ANTHROPIC] Block repr: {repr(block)[:200]}")
                print(f"🟢 [ANTHROPIC] Block repr (first 200 chars): {repr(block)[:200]}")
                
                # Handle case where block might be a string (unexpected API response)
                if isinstance(block, str):
                    logger.warning(f"⚠️ [ANTHROPIC] Block #{block_count} is a STRING: {repr(block[:100])}")
                    print(f"⚠️ [ANTHROPIC] Block #{block_count} is a STRING: {repr(block[:100])}")
                    content += block
                    continue
                
                # Ensure block has type attribute - use getattr for safety
                logger.info(f"🟡 [ANTHROPIC] Block #{block_count} is not a string. Checking for 'type' attribute...")
                print(f"🟡 [ANTHROPIC] Block #{block_count} is not a string. Checking for 'type' attribute...")
                
                try:
                    block_type = getattr(block, 'type', None)
                    logger.info(f"🟡 [ANTHROPIC] Block #{block_count} getattr(block, 'type', None) = {block_type}")
                    print(f"🟡 [ANTHROPIC] Block #{block_count} getattr(block, 'type', None) = {block_type}")
                except Exception as e:
                    logger.error(f"🔴 [ANTHROPIC] ERROR in getattr for block #{block_count}: {e}")
                    print(f"🔴 [ANTHROPIC] ERROR in getattr for block #{block_count}: {e}")
                    raise
                
                if block_type is None:
                    # Block is not a string but also doesn't have type attribute
                    logger.error(f"🔴 [ANTHROPIC] Block #{block_count} missing 'type' attribute. Block type: {type(block)}, Block: {repr(block)[:200]}")
                    print(f"🔴 [ANTHROPIC] Block #{block_count} missing 'type' attribute. Block type: {type(block)}")
                    raise AttributeError(f"Content block missing 'type' attribute: {type(block)}")
                
                # Use getattr for all attribute accesses to avoid AttributeError on strings
                try:
                    if block_type == "text":
                        text_content = getattr(block, 'text', None)
                        if text_content is not None:
                            content += text_content
                        else:
                            logger.warning(f"Text block missing 'text' attribute")
                    elif block_type == "tool_use":
                        tool_id = getattr(block, 'id', None)
                        tool_name = getattr(block, 'name', None)
                        tool_input = getattr(block, 'input', None)
                        
                        if tool_id and tool_name is not None and tool_input is not None:
                            tool_calls.append(
                                ToolCall(
                                    id=tool_id, name=tool_name, arguments=tool_input
                                )
                            )
                        else:
                            logger.error(f"Tool use block missing required attributes: id={tool_id}, name={tool_name}, input={tool_input}")
                    else:
                        logger.warning(f"Unknown block type: {block_type}")
                except (AttributeError, TypeError) as e:
                    logger.error(f"Error accessing block attributes: {e}, Block type: {type(block)}, Block type attr: {block_type}, Block: {repr(block)[:200]}")
                    raise AttributeError(f"Error processing block: {e}") from e

            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens
                    + response.usage.output_tokens,
                },
            )

        except Exception as e:
            logger.error(f"🔴 [ANTHROPIC] API error: {e}", exc_info=True)
            print(f"🔴 [ANTHROPIC] API error: {e}")
            import traceback
            print(f"🔴 [ANTHROPIC] Full traceback:")
            traceback.print_exc()
            raise

    def stream_chat(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ):
        """Stream chat responses (for future use)"""
        raise NotImplementedError("Streaming not yet implemented")
