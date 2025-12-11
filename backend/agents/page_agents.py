"""
Page Generator Agents
Specialized agents for different page types (dashboard, list, detail, form, settings)
"""

from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class PageAgentFactory:
    """Factory to create appropriate page agent based on page type"""
    
    @staticmethod
    def create(page_type: str, client) -> 'BasePageAgent':
        agents = {
            "dashboard": DashboardPageAgent,
            "list": ListPageAgent,
            "detail": DetailPageAgent,
            "form": FormPageAgent,
            "settings": SettingsPageAgent,
            "auth": AuthPageAgent
        }
        agent_class = agents.get(page_type, GenericPageAgent)
        return agent_class(client)


class BasePageAgent(BaseAgent):
    """Base class for page generation agents"""
    
    def __init__(self, client):
        super().__init__(client, model_tier="balanced")
        self.page_type = "generic"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete wireframe page with validation and retry"""
        import asyncio
        
        page = context.get('page', {})
        components = context.get('components', {})
        theme = context.get('theme', {})
        project_context = context.get('project_context', '')
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(page, components, theme, project_context)
        
        # Try up to max_retries times to get valid HTML
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await self.call_llm(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=8000,
                    temperature=0.3  # Lower temperature for more consistent output
                )
                
                html = self.extract_html(response)
                
                # Validate the HTML
                is_valid, error_msg = self.validate_html(html)
                
                if is_valid:
                    print(f"[{self.name}] HTML validation passed")
                    return {
                        "id": page.get('id', 'page'),
                        "name": page.get('name', 'Page'),
                        "type": page.get('type', self.page_type),
                        "html": self._wrap_page(html, components),
                        "description": page.get('description', '')
                    }
                else:
                    print(f"[{self.name}] HTML validation failed (attempt {attempt}): {error_msg}")
                    last_error = ValueError(error_msg)
                    
                    if attempt < self.max_retries:
                        # Add stricter instructions for retry
                        user_prompt = self._get_retry_prompt(page, components, theme, project_context, error_msg)
                        await asyncio.sleep(1)
                        
            except Exception as e:
                last_error = e
                print(f"[{self.name}] Attempt {attempt} error: {str(e)}")
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
        
        # All retries failed - return fallback wireframe
        print(f"[{self.name}] All attempts failed, using fallback wireframe")
        return {
            "id": page.get('id', 'page'),
            "name": page.get('name', 'Page'),
            "type": page.get('type', self.page_type),
            "html": self._wrap_page(self._get_fallback_content(page), components),
            "description": page.get('description', '')
        }
    
    def _get_retry_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str, error: str) -> str:
        """Generate a stricter prompt for retry attempts"""
        return f"""IMPORTANT: Your previous response was invalid. Error: {error}

You MUST return ONLY raw HTML code - no explanations, no markdown, no descriptions.

Create a LOW-FIDELITY WIREFRAME for: {page.get('name', 'Page')}
Type: {self.page_type}
Context: {project_context}

RULES:
1. Start with <div> or <main> tag
2. Use ONLY inline styles (no Tailwind, no external CSS)
3. Grayscale colors only (#fff, #f5f5f5, #e5e5e5, #ccc, #999, #666, #333)
4. Simple layout with placeholder content
5. NO explanatory text before or after the HTML
6. NO markdown code blocks

Return ONLY the HTML content."""

    def _get_fallback_content(self, page: Dict) -> str:
        """Return a basic fallback wireframe when generation fails"""
        page_name = page.get('name', 'Page')
        return f'''<main style="padding: 24px;">
    <div style="margin-bottom: 24px;">
        <h1 style="font-size: 24px; color: #333; margin: 0;">{page_name}</h1>
        <p style="color: #666; margin-top: 8px;">Wireframe content area</p>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px;">
        <div style="background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 16px;">
            <div style="background: #e5e5e5; height: 40px; width: 40px; border-radius: 4px; margin-bottom: 12px;"></div>
            <div style="font-size: 14px; color: #666;">Metric Label</div>
            <div style="font-size: 24px; color: #333; font-weight: bold;">--</div>
        </div>
        <div style="background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 16px;">
            <div style="background: #e5e5e5; height: 40px; width: 40px; border-radius: 4px; margin-bottom: 12px;"></div>
            <div style="font-size: 14px; color: #666;">Metric Label</div>
            <div style="font-size: 24px; color: #333; font-weight: bold;">--</div>
        </div>
        <div style="background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 16px;">
            <div style="background: #e5e5e5; height: 40px; width: 40px; border-radius: 4px; margin-bottom: 12px;"></div>
            <div style="font-size: 14px; color: #666;">Metric Label</div>
            <div style="font-size: 24px; color: #333; font-weight: bold;">--</div>
        </div>
    </div>
    
    <div style="background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 16px;">
        <h2 style="font-size: 18px; color: #333; margin: 0 0 16px 0;">Content Section</h2>
        <div style="background: #f5f5f5; border: 2px dashed #ccc; height: 200px; display: flex; align-items: center; justify-content: center; color: #999;">
            Content Placeholder
        </div>
    </div>
</main>'''
    
    def _get_system_prompt(self) -> str:
        return """You are a wireframe generator. You output ONLY raw HTML code - nothing else.

CRITICAL RULES:
- Output ONLY HTML - no explanations, no descriptions, no markdown
- Do NOT describe what you're creating
- Do NOT add text like "This wireframe includes..." 
- Start directly with HTML tags
- End with closing HTML tags

WIREFRAME STYLE:
1. GRAYSCALE ONLY:
   - Backgrounds: #f5f5f5, #ffffff, #e5e5e5
   - Borders: #ddd, #ccc, #999
   - Text: #333 (headings), #666 (body), #999 (muted)
   
2. SIMPLE INLINE CSS ONLY (no Tailwind, no external CSS):
   - border: 1px solid #ddd
   - background: #fff
   - padding: 16px
   - margin: 0
   - display: flex/grid
   - border-radius: 4px
   - font-family: Arial, sans-serif

3. RESPONSIVE DESIGN (CRITICAL):
   - Use percentage widths: width: 100%, max-width: 1200px
   - Use flexbox with wrap: display: flex; flex-wrap: wrap
   - Use CSS Grid with auto-fit: grid-template-columns: repeat(auto-fit, minmax(280px, 1fr))
   - Avoid fixed pixel widths for containers
   - Cards should be min-width: 280px with flex: 1
   - Tables should have: width: 100%; overflow-x: auto on wrapper
   - Use relative units where possible

4. PLACEHOLDER CONTENT:
   - Images: <div style="background:#e5e5e5;border:2px dashed #ccc;height:100px;display:flex;align-items:center;justify-content:center;color:#999;">[Image]</div>
   - Icons: [icon] or ■ □ ● ○
   - Text: "Heading Text", "Description here", "Label"

4. STRUCTURE:
   - Use <main>, <section>, <div> for layout
   - Simple cards with white background and borders
   - Basic tables with border styling
   - Form inputs with borders

OUTPUT: Raw HTML only. No markdown. No explanations."""

    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create the main content for a {self.page_type} page.

PAGE INFO:
- Name: {page.get('name', 'Page')}
- Description: {page.get('description', 'No description')}

PROJECT CONTEXT:
{project_context}

Generate a BEAUTIFUL, COMPLETE UI with:
- Professional layout with proper visual hierarchy
- All Tailwind classes included (no missing styles)
- Realistic placeholder data
- Proper spacing, colors, and typography"""
    
    def _wrap_page(self, content: str, components: Dict) -> str:
        """Wrap page content with wireframe HTML structure - simple inline CSS only"""
        sidebar = components.get('sidebar', '')
        header = components.get('header', '')
        
        # Simple wireframe CSS - no external dependencies, RESPONSIVE design
        wireframe_css = '''
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; color: #333; line-height: 1.5; }
        .wireframe-container { display: flex; min-height: 100vh; }
        .wireframe-sidebar { width: 220px; min-width: 220px; background: #fff; border-right: 2px solid #ddd; padding: 20px; }
        .wireframe-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
        .wireframe-header { background: #fff; border-bottom: 2px solid #ddd; padding: 15px 20px; }
        .wireframe-content { flex: 1; padding: 20px; background: #f5f5f5; overflow-x: auto; }
        
        /* Wireframe UI Elements */
        .wf-card { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 15px; }
        .wf-btn { display: inline-block; padding: 8px 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 4px; color: #333; cursor: pointer; }
        .wf-btn-primary { background: #666; color: #fff; border-color: #555; }
        .wf-input { padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; background: #fff; width: 100%; }
        .wf-label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; font-size: 12px; }
        .wf-heading { color: #333; margin-bottom: 10px; }
        .wf-text { color: #666; }
        .wf-text-sm { font-size: 12px; color: #888; }
        .wf-divider { border-top: 1px solid #ddd; margin: 15px 0; }
        
        /* Placeholder styles */
        .wf-placeholder { background: #e5e5e5; border: 2px dashed #bbb; display: flex; align-items: center; justify-content: center; color: #888; font-size: 12px; min-height: 100px; }
        .wf-avatar { width: 40px; height: 40px; background: #ddd; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #888; font-size: 14px; flex-shrink: 0; }
        
        /* RESPONSIVE Layout helpers */
        .flex { display: flex; flex-wrap: wrap; }
        .flex-col { flex-direction: column; }
        .items-center { align-items: center; }
        .justify-between { justify-content: space-between; }
        .gap-10 { gap: 10px; }
        .gap-15 { gap: 15px; }
        .gap-20 { gap: 20px; }
        
        /* RESPONSIVE Grids - auto-fit for automatic wrapping */
        .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }
        .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
        
        .mb-10 { margin-bottom: 10px; }
        .mb-15 { margin-bottom: 15px; }
        .mb-20 { margin-bottom: 20px; }
        .p-15 { padding: 15px; }
        .w-full { width: 100%; }
        
        /* RESPONSIVE Table wireframe */
        .table-wrapper { width: 100%; overflow-x: auto; }
        table { width: 100%; min-width: 600px; border-collapse: collapse; background: #fff; }
        th { text-align: left; padding: 10px; background: #f5f5f5; border: 1px solid #ddd; font-size: 11px; text-transform: uppercase; color: #666; white-space: nowrap; }
        td { padding: 10px; border: 1px solid #ddd; }
        
        /* Nav items */
        .wf-nav-item { display: flex; align-items: center; gap: 10px; padding: 10px; border-radius: 4px; color: #555; margin-bottom: 5px; }
        .wf-nav-item:hover { background: #f0f0f0; }
        .wf-nav-item.active { background: #e8e8e8; color: #333; }
        
        /* RESPONSIVE: Hide sidebar on small screens */
        @media (max-width: 768px) {
            .wireframe-sidebar { display: none; }
            .wireframe-content { padding: 15px; }
            .grid-4 { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
        }
        '''
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wireframe</title>
    <style>{wireframe_css}</style>
</head>
<body>
    <div class="wireframe-container">
        {sidebar}
        <div class="wireframe-main">
            {header}
            <div class="wireframe-content">
                {content}
            </div>
        </div>
    </div>
</body>
</html>'''


class DashboardPageAgent(BasePageAgent):
    """Generates dashboard/overview pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "dashboard"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for a Dashboard page.

PAGE: {page.get('name', 'Dashboard')}
CONTEXT: {project_context}

Use the wireframe CSS classes provided (wf-card, wf-btn, wf-heading, wf-placeholder, grid-4, etc.)

RESPONSIVE DESIGN - Use these responsive patterns:
- Use grid-4 class for KPI cards (auto-wraps on smaller screens)
- Use grid-2 class for charts (auto-wraps to single column)
- Wrap tables in <div class="table-wrapper"> for horizontal scroll
- Avoid fixed pixel widths on containers

Include these wireframe sections:
1. PAGE HEADER: Simple heading with placeholder date text
2. KPI CARDS ROW (class="grid-4"): 4 simple cards with:
   - Label text (e.g., "Total Users")
   - Large number placeholder
   - Small change indicator text
3. CHARTS SECTION (class="grid-2"): 2 placeholder boxes for charts
   - Use wf-placeholder class with "Chart Area" text inside
   - Make them about 200px tall
4. RECENT ACTIVITY TABLE (wrapped in table-wrapper):
   - Simple table with columns: Item, Status, Date, Action
   - 4-5 placeholder rows

Keep it SIMPLE - grayscale, no colors, RESPONSIVE, sketch-like appearance."""


class ListPageAgent(BasePageAgent):
    """Generates list/table pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "list"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for a List/Table page.

PAGE: {page.get('name', 'Items')}
CONTEXT: {project_context}

Use the wireframe CSS classes provided (wf-card, wf-btn, wf-input, wf-heading, etc.)

RESPONSIVE DESIGN - Use these responsive patterns:
- Wrap filters in flex container with flex-wrap
- MUST wrap table in <div class="table-wrapper"> for horizontal scroll on mobile
- Use width: 100% on inputs
- Filters should stack on mobile

Include these wireframe sections:
1. PAGE HEADER: Title and "Add New" button (wf-btn wf-btn-primary)
2. FILTERS BAR (wf-card, use class="flex gap-10" with flex-wrap): 
   - Search input (wf-input, style="max-width:300px") 
   - 2-3 filter dropdowns
3. DATA TABLE (MUST be inside <div class="table-wrapper">):
   - Simple table with headers
   - 5-6 columns relevant to context
   - 5 placeholder data rows
   - Action column with "Edit | Delete" text links
4. PAGINATION:
   - "Showing 1-10 of 50" text
   - Simple page number links

Keep it SIMPLE - grayscale, basic table, RESPONSIVE, sketch-like appearance."""


class DetailPageAgent(BasePageAgent):
    """Generates detail/view pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "detail"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for a Detail page.

PAGE: {page.get('name', 'Item Detail')}
CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-heading, wf-placeholder, etc.)

Include:
1. BREADCRUMB: Simple text "Home > List > Detail"
2. PAGE HEADER: Back button, title, action buttons
3. MAIN INFO CARD: Image placeholder on left, details grid on right
4. DETAILS SECTION: 2-column labeled values
5. RELATED ITEMS: Simple list or small cards

Keep it SIMPLE - grayscale, sketch-like appearance."""


class FormPageAgent(BasePageAgent):
    """Generates form pages (create/edit)"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "form"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for a Form page.

PAGE: {page.get('name', 'Create/Edit')}
CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-input, wf-label, etc.)

Include:
1. PAGE HEADER: Title and Cancel/Save buttons
2. FORM CARD with sections:
   - Form fields with labels (wf-label + wf-input)
   - 2-column layout for fields
   - Text areas
3. FOOTER: Cancel and Save buttons

Keep it SIMPLE - grayscale, basic form, sketch-like appearance."""


class SettingsPageAgent(BasePageAgent):
    """Generates settings/configuration pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "settings"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for a Settings page.

PAGE: {page.get('name', 'Settings')}
CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-input, etc.)

Include:
1. Settings navigation on left (simple list)
2. Settings content on right:
   - Section titles
   - Toggle placeholders [On/Off]
   - Input fields
3. Save button at bottom

Keep it SIMPLE - grayscale, sketch-like appearance."""


class AuthPageAgent(BasePageAgent):
    """Generates authentication pages (login/register)"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "auth"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for an Auth page.

PAGE: {page.get('name', 'Login')}

This is a FULL PAGE (no sidebar/header).

Include:
1. Centered card with:
   - Logo placeholder
   - Title "Sign In"
   - Email input
   - Password input
   - Login button
   - "Forgot password?" link
   - "Sign up" link

Keep it SIMPLE - grayscale, basic form, sketch-like appearance."""
    
    def _wrap_page(self, content: str, components: Dict) -> str:
        """Auth pages - simple wireframe style"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: #f0f0f0; color: #333; min-height: 100vh; display: flex; align-items: center; justify-content: center; }}
        .wf-card {{ background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 30px; max-width: 400px; width: 100%; }}
        .wf-btn {{ display: block; width: 100%; padding: 12px; background: #666; color: #fff; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; }}
        .wf-input {{ display: block; width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-top: 5px; }}
        .wf-label {{ display: block; margin-top: 15px; font-size: 13px; color: #555; }}
        .wf-heading {{ font-size: 24px; margin-bottom: 20px; text-align: center; }}
        .wf-text {{ color: #666; font-size: 13px; text-align: center; margin-top: 15px; }}
        .wf-placeholder {{ background: #e5e5e5; border: 2px dashed #bbb; padding: 20px; text-align: center; color: #888; }}
    </style>
</head>
<body>
    {content}
</body>
</html>'''


class GenericPageAgent(BasePageAgent):
    """Fallback for unknown page types"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "generic"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        return f"""Create a LOW-FIDELITY WIREFRAME for: {page.get('name', 'Page')}

Description: {page.get('description', 'Generic page')}
CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-heading, etc.)

Create a simple layout with:
- Page heading
- Content sections using wf-card
- Placeholder areas

Keep it SIMPLE - grayscale, sketch-like appearance."""
