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
        
        system_prompt = """You are a wireframe component generator. Create SIMPLE wireframe components with inline CSS only.

CRITICAL RULES:
1. DO NOT use Tailwind CSS - use ONLY inline styles and wireframe classes (wf-nav-item, wf-btn, wf-avatar)
2. Grayscale colors only: #fff, #f5f5f5, #e5e5e5, #ddd, #ccc, #999, #666, #333
3. For icons: Use text placeholders [icon], [menu], [bell], [search], [user] - NO SVG
4. All navigation links MUST use: <a href="#" class="wf-nav-item">
5. Header must have: style="display: flex; align-items: center; justify-content: space-between;"
6. Keep it SIMPLE - low-fidelity wireframe style

STRUCTURE:
- Sidebar: <aside class="wireframe-sidebar"> with wf-nav-item links
- Header: <header class="wireframe-header" style="display:flex..."> with left/right sections
- Use semantic HTML

Return a JSON object with these keys:
- sidebar: Complete sidebar HTML
- header: Complete header HTML  
- page_wrapper: Template for page content wrapper

Do not include ```json markers. Return pure JSON."""

        user_prompt = f"""Create shared wireframe UI components with:

NAVIGATION ITEMS:
{sidebar_items}

WIREFRAME RULES - PURE GRAYSCALE ONLY:
- White backgrounds: #fff, #f5f5f5
- Light grays: #e5e5e5, #ddd, #ccc
- Dark grays: #999, #666, #333
- NO COLORS - only black, white, and gray shades
- NO brand colors, NO blues, NO theme colors

Create SIMPLE wireframe components:
1. SIDEBAR: White background (#fff), gray borders (#ddd), simple nav items
2. HEADER: White background (#fff), gray border bottom (#ddd), basic layout
3. PAGE_WRAPPER: Light gray background (#f5f5f5)

Keep it MINIMAL - low-fidelity sketch style, black and white only.

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
