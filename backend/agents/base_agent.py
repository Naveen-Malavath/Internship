"""
Base Agent Class
Foundation for all wireframe generation agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from anthropic import Anthropic
import os
import json


class BaseAgent(ABC):
    """Base class for all agents in the wireframe system"""
    
    # Model configurations - use Claude Haiku 4.5 for fast, quality output
    MODELS = {
        "fast": "claude-haiku-4-5-20251001",      # For simple tasks (planning)
        "balanced": "claude-haiku-4-5-20251001",  # For complex tasks (HTML generation)
        "premium": "claude-haiku-4-5-20251001"    # For critical tasks
    }
    
    def __init__(self, client: Anthropic, model_tier: str = "balanced"):
        self.client = client
        self.model = self.MODELS.get(model_tier, self.MODELS["balanced"])
        self.name = self.__class__.__name__
        self.max_retries = 3
        
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass
    
    async def call_llm(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Call the LLM with given prompts and retry logic"""
        import asyncio
        
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"[{self.name}] Calling {self.model}... (Attempt {attempt}/{self.max_retries})")
                
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                
                response = message.content[0].text
                print(f"[{self.name}] Response received ({len(response)} chars)")
                return response
                
            except Exception as e:
                last_error = e
                print(f"[{self.name}] Attempt {attempt} failed: {str(e)}")
                
                if attempt < self.max_retries:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = 2 ** (attempt - 1)
                    print(f"[{self.name}] Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        
        # All retries failed
        print(f"[{self.name}] All {self.max_retries} attempts failed")
        raise last_error
    
    def parse_json(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response, handling markdown code blocks"""
        # Remove markdown code blocks if present
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    
    def extract_html(self, response: str) -> str:
        """Extract HTML from LLM response, handling markdown code blocks"""
        text = response.strip()
        
        # Remove markdown code blocks
        if text.startswith("```html"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        # Try to extract just the HTML if there's extra text
        # Look for <!DOCTYPE or <html or first tag
        import re
        
        # If response contains <!DOCTYPE or <html, extract from there
        doctype_match = re.search(r'(<!DOCTYPE\s+html[^>]*>)', text, re.IGNORECASE)
        html_match = re.search(r'(<html[^>]*>)', text, re.IGNORECASE)
        
        if doctype_match:
            start_idx = doctype_match.start()
            text = text[start_idx:]
        elif html_match:
            start_idx = html_match.start()
            text = text[start_idx:]
        
        # Remove any trailing text after </html>
        html_end = text.lower().rfind('</html>')
        if html_end != -1:
            text = text[:html_end + 7]
        
        return text.strip()
    
    def validate_html(self, html: str) -> tuple[bool, str]:
        """Validate that the response is valid HTML for a wireframe"""
        if not html:
            return False, "Empty HTML response"
        
        html_lower = html.lower()
        
        # Must have basic HTML structure
        if '<div' not in html_lower and '<section' not in html_lower and '<main' not in html_lower:
            return False, "No HTML content elements found (div, section, main)"
        
        # Should not be mostly text/explanation
        text_indicators = ['this wireframe', 'this low-fidelity', 'includes:', 'features:', 
                          'the design', 'i have created', 'here is', 'this page']
        text_count = sum(1 for indicator in text_indicators if indicator in html_lower)
        if text_count >= 3:
            return False, "Response appears to be explanatory text, not HTML"
        
        # Check for reasonable HTML length (at least some content)
        if len(html) < 100:
            return False, f"HTML too short ({len(html)} chars)"
        
        return True, "Valid"
