"""
Design System Agent
Creates shared UI components (sidebar, header, footer) for consistency
"""

from typing import Dict, Any
from .base_agent import BaseAgent


class DesignSystemAgent(BaseAgent):
    """Generates reusable UI components"""
    
    def __init__(self, client):
        super().__init__(client, model_tier="balanced")  # Use Sonnet for quality
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate shared UI components
        
        Input context:
            - plan: output from PlanningAgent
            
        Output:
            - sidebar: HTML for sidebar component
            - header: HTML for header component
            - styles: Shared CSS/Tailwind utilities
        """
        
        plan = context.get('plan', {})
        navigation = plan.get('navigation', {})
        theme = plan.get('theme', {})
        sidebar_items = navigation.get('sidebar_items', [])
        
        system_prompt = """You are a senior UI developer creating reusable HTML/Tailwind CSS components.

Create professional, modern, dark-themed components that will be reused across all wireframe pages.

Requirements:
1. Use Tailwind CSS classes only (no custom CSS)
2. Dark theme with the provided colors
3. Responsive design
4. Include hover/active states
5. Modern, clean aesthetic
6. Include placeholder icons using text or simple SVG

Return a JSON object with these keys:
- sidebar: Complete sidebar HTML
- header: Complete header HTML  
- page_wrapper: Template for page content wrapper

Do not include ```json markers. Return pure JSON."""

        user_prompt = f"""Create shared UI components with:

NAVIGATION ITEMS:
{sidebar_items}

THEME COLORS:
- Background: {theme.get('background', '#0f172a')}
- Primary: {theme.get('primary_color', '#3b82f6')}
- Secondary: {theme.get('secondary_color', '#1e293b')}
- Text: {theme.get('text_color', '#e2e8f0')}
- Accent: {theme.get('accent_color', '#60a5fa')}

Create:
1. SIDEBAR: Vertical navigation with icons and labels, collapsible, active states
2. HEADER: Top bar with logo, search, notifications, user menu
3. PAGE_WRAPPER: Container for main content with proper spacing

Return JSON with sidebar, header, page_wrapper keys containing HTML strings."""

        response = await self.call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=4000,
            temperature=0.5
        )
        
        try:
            components = self.parse_json(response)
            print(f"[{self.name}] Generated {len(components)} components")
            return components
        except Exception as e:
            print(f"[{self.name}] JSON parse error, using defaults: {e}")
            return self._get_default_components(theme, sidebar_items)
    
    def _get_default_components(self, theme: Dict, sidebar_items: list) -> Dict[str, str]:
        """Return default wireframe-style components"""
        
        # Generate sidebar items HTML - simple wireframe style
        items_html = ""
        for i, item in enumerate(sidebar_items[:6]):
            active_class = "active" if i == 0 else ""
            items_html += f'''
            <a href="#" class="wf-nav-item {active_class}">
                <span>[icon]</span>
                <span>{item.get('name', 'Item')}</span>
            </a>'''
        
        return {
            "sidebar": f'''
<aside class="wireframe-sidebar">
    <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">
        <h1 style="font-size: 18px; font-weight: bold; color: #333; display: flex; align-items: center; gap: 10px;">
            <span style="width: 32px; height: 32px; background: #ddd; border: 1px solid #ccc; display: flex; align-items: center; justify-content: center; border-radius: 4px;">W</span>
            App Name
        </h1>
    </div>
    <nav>
        {items_html}
    </nav>
    <div style="margin-top: auto; padding-top: 15px; border-top: 1px solid #ddd;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div class="wf-avatar">U</div>
            <div>
                <p style="font-size: 13px; color: #333;">User Name</p>
                <p style="font-size: 11px; color: #888;">user@email.com</p>
            </div>
        </div>
    </div>
</aside>''',
            
            "header": '''
<header class="wireframe-header" style="display: flex; align-items: center; justify-content: space-between;">
    <div style="display: flex; align-items: center; gap: 15px;">
        <button class="wf-btn">[Menu]</button>
        <input type="text" class="wf-input" placeholder="Search..." style="width: 250px;">
    </div>
    <div style="display: flex; align-items: center; gap: 15px;">
        <button class="wf-btn">[Bell]</button>
        <div class="wf-avatar">U</div>
    </div>
</header>''',
            
            "page_wrapper": '''
<main class="wireframe-content">
    <!-- Page content goes here -->
</main>'''
        }
