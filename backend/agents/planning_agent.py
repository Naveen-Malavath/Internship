"""
Planning Agent
Analyzes project context and determines required wireframe pages
Maps features and user stories to specific UI pages
"""

from typing import Dict, Any, List
from .base_agent import BaseAgent


class PlanningAgent(BaseAgent):
    """Plans wireframe pages based on project features and user stories"""
    
    def __init__(self, client):
        super().__init__(client, model_tier="balanced")  # Use Sonnet for better analysis
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project features and stories to plan wireframe pages
        
        Input context:
            - project_summary: str
            - features_summary: str (full feature details)
            - stories_summary: str (user stories)
            - hld_summary: str
            - api_summary: str
            - page_mode: 'auto' | 'manual'
            - page_count: int (when manual mode)
            
        Output:
            - pages: list with feature mapping
            - navigation: navigation structure
            - theme: theme configuration
        """
        
        page_mode = context.get('page_mode', 'auto')
        page_count = context.get('page_count', 5)
        
        # Build page count instruction based on mode
        if page_mode == 'manual':
            page_instruction = f"""IMPORTANT: Generate EXACTLY {page_count} pages.
Select the {page_count} most important pages based on the features provided.
Prioritize pages that cover the core user workflows."""
        else:
            page_instruction = """Analyze each feature and determine what UI pages it needs.
Create pages that directly implement the features and user stories.
Generate between 4-10 pages based on feature count."""
        
        system_prompt = f"""You are a UI/UX architect specializing in feature-driven design.

TASK: Analyze the provided features and user stories to create a page plan where EACH PAGE directly implements specific features/stories.

CRITICAL: Each page must be traceable to actual features and stories from the input. Do NOT create generic pages.

You must respond with ONLY valid JSON (no markdown, no explanations):

{{
    "pages": [
        {{
            "id": "unique-page-id",
            "name": "Descriptive Page Name",
            "type": "dashboard|list|detail|form|settings|auth",
            "description": "What this page does",
            "priority": 1,
            "related_features": ["Feature Title 1", "Feature Title 2"],
            "related_stories": ["Story Title 1", "Story Title 2"],
            "functionality": [
                "Specific function 1 from the features",
                "Specific function 2 from the stories"
            ],
            "ui_elements": ["element1", "element2"],
            "data_displayed": ["data1", "data2"]
        }}
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

Page Type Guide:
- dashboard: Overview/analytics pages with KPIs, charts, summaries
- list: Data listings (products, orders, users, etc.) with filters, search, pagination
- detail: Single item view (order details, product page, user profile)
- form: Create/Edit forms (new product, edit profile, checkout)
- settings: Configuration/preferences pages
- auth: Login, Register, Password Reset

RULES:
1. Page names must reflect actual features (e.g., "Order History" not "List Page")
2. related_features must contain EXACT feature titles from the input
3. related_stories must contain EXACT story titles from the input
4. functionality must list specific functions from the feature descriptions
5. Each feature should map to at least one page

{page_instruction}

Return ONLY valid JSON."""

        # Build comprehensive context for planning
        context_parts = []
        
        if context.get('project_summary'):
            context_parts.append(f"PROJECT SUMMARY:\n{context['project_summary']}")
        
        if context.get('features_summary'):
            context_parts.append(f"APPROVED FEATURES (create pages for these):\n{context['features_summary']}")
        
        if context.get('stories_summary'):
            context_parts.append(f"USER STORIES (implement these in the pages):\n{context['stories_summary']}")
        
        if context.get('hld_summary'):
            context_parts.append(f"HIGH LEVEL DESIGN:\n{context['hld_summary']}")
        
        if context.get('api_summary'):
            context_parts.append(f"API DESIGN:\n{context['api_summary']}")
        
        if context.get('architecture_context'):
            context_parts.append(f"ARCHITECTURE DETAILS:\n{context['architecture_context']}")
        
        full_context = "\n\n".join(context_parts) if context_parts else "No project context provided"
        
        user_prompt = f"""Analyze this project and create a page plan:

{full_context}

INSTRUCTIONS:
1. Read each feature and its acceptance criteria
2. Read each user story and understand what UI it needs
3. Create pages that implement these features/stories
4. Map each page to specific features and stories it implements
5. Include specific functionality based on the acceptance criteria

Return ONLY valid JSON with feature-mapped pages."""

        response = await self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4000,
            temperature=0.3
        )
        
        try:
            plan = self.parse_json(response)
            
            # Ensure all pages have required fields
            for page in plan.get('pages', []):
                if 'related_features' not in page:
                    page['related_features'] = []
                if 'related_stories' not in page:
                    page['related_stories'] = []
                if 'functionality' not in page:
                    page['functionality'] = [page.get('description', '')]
                if 'ui_elements' not in page:
                    page['ui_elements'] = []
                if 'data_displayed' not in page:
                    page['data_displayed'] = []
            
            print(f"[{self.name}] Planned {len(plan.get('pages', []))} feature-mapped pages")
            return plan
        except Exception as e:
            print(f"[{self.name}] JSON parse error, using defaults: {e}")
            return self._get_default_plan(context)
    
    def _get_default_plan(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Return a context-aware default plan if parsing fails"""
        # Try to extract feature names from context
        features_summary = context.get('features_summary', '') if context else ''
        
        # Create basic pages based on common patterns
        pages = [
            {
                "id": "dashboard", 
                "name": "Dashboard", 
                "type": "dashboard", 
                "description": "Main overview with key metrics",
                "priority": 1,
                "related_features": [],
                "related_stories": [],
                "functionality": ["View key metrics", "See recent activity"],
                "ui_elements": ["KPI cards", "Charts", "Activity feed"],
                "data_displayed": ["Statistics", "Recent items"]
            }
        ]
        
        # If we have features, add a generic list page
        if features_summary:
            pages.append({
                "id": "main-list", 
                "name": "Main List", 
                "type": "list", 
                "description": "Primary data listing",
                "priority": 2,
                "related_features": [],
                "related_stories": [],
                "functionality": ["View items", "Search", "Filter"],
                "ui_elements": ["Data table", "Search bar", "Filters"],
                "data_displayed": ["List items"]
            })
        
        return {
            "pages": pages,
            "navigation": {
                "sidebar_items": [
                    {"id": page["id"], "name": page["name"], "icon": "folder"} 
                    for page in pages
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
