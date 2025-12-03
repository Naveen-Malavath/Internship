"""
Planning Agent
Analyzes project context and determines required wireframe pages
Uses Haiku for fast, cost-effective planning
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    """Plans wireframe pages based on project context"""
    
    def __init__(self, client):
        super().__init__(client, model_tier="fast")  # Use Haiku for speed
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project and plan wireframe pages
        
        Input context:
            - project_summary: str
            - features: list
            - hld_summary: str
            - api_summary: str
            - page_mode: 'auto' | 'manual'
            - page_count: int (when manual mode)
            
        Output:
            - pages: list of page definitions
            - navigation: navigation structure
            - theme: theme configuration
        """
        
        page_mode = context.get('page_mode', 'auto')
        page_count = context.get('page_count', 5)
        
        # Build page count instruction based on mode
        if page_mode == 'manual':
            page_instruction = f"""IMPORTANT: Generate EXACTLY {page_count} pages.
Distribute page types appropriately based on the project needs.
Include a mix of: dashboard, list, detail, form, settings pages as needed."""
        else:
            page_instruction = """Analyze the project complexity and determine the OPTIMAL number of pages.
Consider:
- Number of features/modules in the project
- API endpoints that need UI
- User roles and their different views
- Core workflows that need screens

Generate between 3-12 pages based on project complexity.
Simpler projects: 3-5 pages
Medium projects: 5-8 pages  
Complex projects: 8-12 pages"""
        
        system_prompt = f"""You are a UI/UX architect. Analyze the project and determine the wireframe pages needed.

You must respond with ONLY valid JSON, no markdown code blocks, no explanations.

The JSON structure must be:
{{
    "pages": [
        {{"id": "page-id", "name": "Page Name", "type": "dashboard|list|detail|form|settings|auth", "description": "Brief description", "priority": 1}}
    ],
    "navigation": {{
        "sidebar_items": [{{"id": "page-id", "name": "Page Name", "icon": "icon-name"}}],
        "user_menu": ["Profile", "Settings", "Logout"]
    }},
    "theme": {{
        "primary_color": "#3b82f6",
        "secondary_color": "#1e293b", 
        "background": "#0f172a",
        "text_color": "#e2e8f0",
        "accent_color": "#60a5fa"
    }}
}}

Page types:
- dashboard: Overview with KPIs, charts, activity
- list: Data table with filters, search, pagination
- detail: Single item view with info sections
- form: Create/Edit forms
- settings: Configuration page
- auth: Login/Register pages

{page_instruction}

Return ONLY valid JSON."""

        user_prompt = f"""Analyze this project and plan the wireframe pages:

PROJECT SUMMARY:
{context.get('project_summary', 'No summary provided')}

FEATURES:
{context.get('features_summary', 'No features provided')}

HIGH LEVEL DESIGN:
{context.get('hld_summary', 'No HLD provided')}

API DESIGN:
{context.get('api_summary', 'No API design provided')}

Determine the essential wireframe pages needed for this application.
Return ONLY valid JSON."""

        response = await self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2000,
            temperature=0.3  # Lower temperature for consistent structure
        )
        
        try:
            plan = self.parse_json(response)
            print(f"[{self.name}] Planned {len(plan.get('pages', []))} pages")
            return plan
        except Exception as e:
            print(f"[{self.name}] JSON parse error, using defaults: {e}")
            return self._get_default_plan()
    
    def _get_default_plan(self) -> Dict[str, Any]:
        """Return a sensible default plan if parsing fails"""
        return {
            "pages": [
                {"id": "dashboard", "name": "Dashboard", "type": "dashboard", "description": "Main overview", "priority": 1},
                {"id": "items-list", "name": "Items", "type": "list", "description": "List view", "priority": 2}
            ],
            "navigation": {
                "sidebar_items": [
                    {"id": "dashboard", "name": "Dashboard", "icon": "dashboard"},
                    {"id": "items-list", "name": "Items", "icon": "list"}
                ],
                "user_menu": ["Profile", "Settings", "Logout"]
            },
            "theme": {
                "primary_color": "#3b82f6",
                "secondary_color": "#1e293b",
                "background": "#0f172a",
                "text_color": "#e2e8f0",
                "accent_color": "#60a5fa"
            }
        }
