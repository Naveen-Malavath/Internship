"""Shared Claude client helpers."""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from anthropic import AsyncAnthropic
from anthropic.types import Message

logger = logging.getLogger(__name__)

def get_claude_model() -> str:
    """Get Claude model name from environment or use default Sonnet 4.5.
    
    Priority:
    1. CLAUDE_MODEL environment variable
    2. CLAUDE_MODEL_DEBUG environment variable (for testing new models)
    3. Default: claude-sonnet-4-5-20250929 (Claude Sonnet 4.5)
    """
    debug_model = os.getenv("CLAUDE_MODEL_DEBUG")
    if debug_model:
        logger.info(f"[claude_client] Using DEBUG model from CLAUDE_MODEL_DEBUG: {debug_model}")
        return debug_model
    
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
    logger.info(f"[claude_client] Using Claude Sonnet 4.5 model: {model}")
    return model


DEFAULT_CLAUDE_MODEL = get_claude_model()

_client: Optional[AsyncAnthropic] = None


def get_claude_client() -> AsyncAnthropic:
    """Return a singleton AsyncAnthropic client."""
    global _client
    if _client is None:
        api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            logger.error("[claude_client] API key not configured")
            raise RuntimeError("CLAUDE_API_KEY or ANTHROPIC_API_KEY is not configured.")
        _client = AsyncAnthropic(api_key=api_key)
        logger.debug("[claude_client] Claude client initialized")
    return _client


def extract_text(message: Message) -> str:
    """Extract the first text block from a Claude message."""
    for block in message.content:
        if block.type == "text":
            text = block.text
            logger.debug(f"[claude_client] Extracted text block: {len(text)} chars")
            return text
    logger.error("[claude_client] No text block found in Claude response")
    raise RuntimeError("Claude response did not contain a text block.")


def coerce_json(payload: str) -> dict:
    """Parse JSON payload from Claude, raising a helpful error on failure.
    
    Handles markdown code blocks (```json ... ```) that Claude sometimes wraps around JSON.
    Also handles truncated responses by attempting to extract valid JSON from partial content.
    """
    logger.debug(f"[claude_client] Parsing JSON payload: {len(payload)} chars")
    logger.debug(f"[claude_client] Payload starts with: {payload[:150]}")
    logger.debug(f"[claude_client] Payload ends with: {payload[-150:] if len(payload) > 150 else payload}")
    original_payload = payload
    stripped = payload.strip()
    logger.debug(f"[claude_client] After initial strip: {len(stripped)} chars")
    
    # Remove markdown code blocks if present - handle various formats
    if stripped.startswith("```"):
        logger.debug("[claude_client] Detected markdown code block, stripping...")
        lines = stripped.split("\n")
        
        # Remove first line (```json, ```JSON, or just ```)
        if len(lines) > 0:
            first_line = lines[0].strip()
            # Remove backticks and language identifier
            if first_line.startswith("```"):
                # Check if there's a language identifier
                lang_part = first_line[3:].strip().lower()
                if lang_part in ["json", "javascript"]:
                    # Language identifier present, remove first line
                    if len(lines) > 1:
                        stripped = "\n".join(lines[1:]).strip()
                    else:
                        stripped = ""
                else:
                    # Just backticks, might be closing or opening
                    if len(lines) > 1:
                        stripped = "\n".join(lines[1:]).strip()
                    else:
                        stripped = first_line.strip("`").strip()
        
        # Remove closing ``` if present (might be missing if truncated)
        if stripped.endswith("```"):
            stripped = stripped[:-3].strip()
        elif stripped.endswith("``"):
            stripped = stripped[:-2].strip()
        elif stripped.endswith("`"):
            stripped = stripped[:-1].strip()
        
        logger.debug(f"[claude_client] After stripping markdown: {len(stripped)} chars, starts with: {stripped[:50]}")
    
    # Try parsing the stripped content directly
    try:
        result = json.loads(stripped)
        logger.debug(f"[claude_client] Successfully parsed JSON directly | result type: {type(result)} | keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"[claude_client] Direct JSON parse failed: {e} | error at position: {getattr(e, 'pos', 'unknown')}")
        logger.debug(f"[claude_client] Trying fallback extraction methods...")
        pass
    
    # Fallback 1: Try to extract JSON between first { and last }
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
        candidate = stripped[first_brace : last_brace + 1]
        logger.debug(f"[claude_client] Trying brace-extracted JSON: {len(candidate)} chars")
        try:
            result = json.loads(candidate)
            logger.debug("[claude_client] Successfully parsed brace-extracted JSON")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"[claude_client] Brace extraction failed: {e}")
            pass
    
    # Fallback 2: Try to find and extract JSON from original payload (in case stripping removed too much)
    if stripped != original_payload.strip():
        first_brace = original_payload.find("{")
        last_brace = original_payload.rfind("}")
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            candidate = original_payload[first_brace : last_brace + 1]
            logger.debug(f"[claude_client] Trying original payload extraction: {len(candidate)} chars")
            try:
                result = json.loads(candidate)
                logger.debug("[claude_client] Successfully parsed from original payload")
                return result
            except json.JSONDecodeError as e:
                logger.debug(f"[claude_client] Original payload extraction failed: {e}")
                pass
    
    # Fallback 3: Try to repair truncated JSON by extracting partial structures
    logger.debug("[claude_client] Attempting to extract partial JSON from potentially truncated response")
    try:
        # Try to find and extract complete features array
        features_start = stripped.find('"features"')
        stories_start = stripped.find('"stories"')
        
        # Determine which array we're looking for
        target_key = None
        target_start = -1
        if features_start != -1 and (stories_start == -1 or features_start < stories_start):
            target_key = "features"
            target_start = features_start
        elif stories_start != -1:
            target_key = "stories"
            target_start = stories_start
        
        if target_start != -1:
            # Find the opening bracket after the key
            bracket_start = stripped.find("[", target_start)
            if bracket_start != -1:
                # Try to find matching closing bracket by counting braces and brackets
                bracket_count = 0
                brace_count = 0
                in_string = False
                escape_next = False
                last_valid_pos = -1
                
                for i in range(bracket_start, len(stripped)):
                    char = stripped[i]
                    
                    if escape_next:
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        continue
                    
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                    
                    if in_string:
                        continue
                    
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0 and brace_count >= 0:
                            # Found complete array
                            last_valid_pos = i
                            break
                
                if last_valid_pos != -1:
                    # Found complete array
                    array_content = stripped[bracket_start:last_valid_pos + 1]
                    try:
                        parsed_array = json.loads(array_content)
                        result = {target_key: parsed_array}
                        logger.warning(f"[claude_client] Successfully parsed complete {target_key} array from response")
                        return result
                    except json.JSONDecodeError as e:
                        logger.debug(f"[claude_client] Complete array extraction failed: {e}")
                
                # If no complete array found, try to extract partial array by finding last complete object
                if last_valid_pos == -1:
                    # Go backwards from the end to find the last complete object
                    brace_depth = 0
                    bracket_depth = 0
                    in_string = False
                    escape_next = False
                    last_complete_obj_end = -1
                    
                    # Start from a reasonable position (after first opening bracket)
                    search_start = min(bracket_start + 100, len(stripped))
                    
                    for i in range(search_start, len(stripped)):
                        char = stripped[i]
                        
                        if escape_next:
                            escape_next = False
                            continue
                        
                        if char == '\\':
                            escape_next = True
                            continue
                        
                        if char == '"' and not escape_next:
                            in_string = not in_string
                            continue
                        
                        if in_string:
                            continue
                        
                        if char == '{':
                            brace_depth += 1
                        elif char == '}':
                            brace_depth -= 1
                            if brace_depth == 0 and bracket_depth == 1:
                                # Found a complete object at current bracket level
                                last_complete_obj_end = i
                        elif char == '[':
                            bracket_depth += 1
                        elif char == ']':
                            bracket_depth -= 1
                    
                    if last_complete_obj_end != -1 and last_complete_obj_end > bracket_start:
                        # Extract up to the last complete object and close the array
                        partial_content = stripped[bracket_start:last_complete_obj_end + 1]
                        # Try to parse as array by adding closing bracket and brace
                        try:
                            # Count existing objects by counting complete braces
                            test_str = partial_content
                            if not test_str.strip().startswith("["):
                                test_str = "[" + test_str
                            if not test_str.strip().endswith("]"):
                                test_str = test_str + "]"
                            parsed_array = json.loads(test_str)
                            if isinstance(parsed_array, list) and len(parsed_array) > 0:
                                result = {target_key: parsed_array}
                                logger.warning(f"[claude_client] Successfully extracted partial {target_key} array with {len(parsed_array)} items")
                                return result
                        except json.JSONDecodeError:
                            pass
    except Exception as e:
        logger.debug(f"[claude_client] Truncated JSON repair failed: {e}", exc_info=True)
    
    # Fallback 4: Try to extract any valid JSON fragments and reconstruct
    try:
        # Find all complete objects in the response
        objects = []
        brace_count = 0
        in_string = False
        escape_next = False
        obj_start = -1
        
        for i, char in enumerate(stripped):
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if in_string:
                continue
            
            if char == '{':
                if brace_count == 0:
                    obj_start = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and obj_start != -1:
                    obj_str = stripped[obj_start:i+1]
                    try:
                        obj = json.loads(obj_str)
                        objects.append(obj)
                    except json.JSONDecodeError:
                        pass
                    obj_start = -1
        
        if objects:
            # Try to determine the key based on object structure
            if objects and isinstance(objects[0], dict):
                first_obj = objects[0]
                if "feature_id" in first_obj or "feature_title" in first_obj or "story_text" in first_obj:
                    result = {"stories": objects}
                    logger.warning(f"[claude_client] Successfully extracted {len(objects)} story objects from truncated response")
                    return result
                elif "title" in first_obj or "description" in first_obj or "acceptanceCriteria" in first_obj:
                    result = {"features": objects}
                    logger.warning(f"[claude_client] Successfully extracted {len(objects)} feature objects from truncated response")
                    return result
    except Exception as e:
        logger.debug(f"[claude_client] Fragment extraction failed: {e}")
    
    # If all else fails, raise with helpful error message
    error_preview = original_payload[:500] if len(original_payload) > 500 else original_payload
    logger.error(f"[claude_client] Failed to parse JSON after all attempts")
    logger.error(f"[claude_client] Payload length: {len(original_payload)} chars")
    logger.error(f"[claude_client] Payload preview (first 500): {error_preview}")
    logger.error(f"[claude_client] Payload preview (last 500): {original_payload[-500:] if len(original_payload) > 500 else original_payload}")
    logger.error(f"[claude_client] Stripped payload length: {len(stripped)} chars")
    raise RuntimeError(
        f"Claude returned invalid or incomplete JSON. "
        f"Response may be truncated. Payload length: {len(original_payload)} chars. "
        f"Preview: {error_preview}..."
    )
