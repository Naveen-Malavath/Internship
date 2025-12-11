"""
Page Generator Agents
Specialized agents for different page types (dashboard, list, detail, form, settings)
Includes Angular component code generation for each page type
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
        """Generate a complete wireframe page with validation, retry, and Angular component code"""
        import asyncio
        
        page = context.get('page', {})
        components = context.get('components', {})
        theme = context.get('theme', {})
        project_context = context.get('project_context', '')
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._get_user_prompt(page, components, theme, project_context)
        
        # Try up to max_retries times to get valid HTML
        last_error = None
        html_result = None
        
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
                    html_result = self._wrap_page(html, components)
                    break
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
        
        # Use fallback if all retries failed
        if html_result is None:
            print(f"[{self.name}] All attempts failed, using fallback wireframe")
            html_result = self._wrap_page(self._get_fallback_content(page), components)
        
        # Generate Angular component code
        print(f"[{self.name}] Generating Angular component code...")
        component_code = await self._generate_angular_component(page, html_result, project_context)
        
        return {
            "id": page.get('id', 'page'),
            "name": page.get('name', 'Page'),
            "type": page.get('type', self.page_type),
            "html": html_result,
            "description": page.get('description', ''),
            "component_ts": component_code.get('typescript', ''),
            "component_html": component_code.get('html', ''),
            "component_scss": component_code.get('scss', '')
        }
    
    async def _generate_angular_component(self, page: Dict, wireframe_html: str, project_context: str) -> Dict[str, str]:
        """Generate Angular component code based on the wireframe"""
        import asyncio
        
        page_name = page.get('name', 'Page')
        page_id = page.get('id', 'page')
        component_name = self._to_pascal_case(page_name)
        selector_name = self._to_kebab_case(page_name)
        
        system_prompt = self._get_angular_system_prompt()
        user_prompt = self._get_angular_user_prompt(page, wireframe_html, project_context)
        
        try:
            response = await self.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=12000,
                temperature=0.3
            )
            
            # Parse the response to extract TS, HTML, and SCSS
            component_code = self._parse_angular_response(response, component_name, selector_name)
            return component_code
            
        except Exception as e:
            print(f"[{self.name}] Angular component generation failed: {str(e)}")
            # Return fallback component code
            return self._get_fallback_angular_component(page, component_name, selector_name)
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase for component class name"""
        words = name.replace('-', ' ').replace('_', ' ').split()
        return ''.join(word.capitalize() for word in words)
    
    def _to_kebab_case(self, name: str) -> str:
        """Convert name to kebab-case for selector"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower().replace(' ', '-').replace('_', '-')
    
    def _get_angular_system_prompt(self) -> str:
        """System prompt for Angular component generation"""
        return """You are an expert Angular developer. Generate production-ready Angular component code.

OUTPUT FORMAT - You MUST return exactly 3 code blocks in this order:
1. ```typescript - The component TypeScript file
2. ```html - The component HTML template
3. ```scss - The component SCSS styles

ANGULAR REQUIREMENTS:
- Use Angular 18+ standalone components
- Use Angular Material components where appropriate
- Use reactive forms (FormGroup, FormControl) for forms
- Use signals for state management where appropriate
- Include proper TypeScript types and interfaces
- Use @Input() and @Output() decorators for component communication
- Include OnInit, OnDestroy lifecycle hooks as needed
- Use proper dependency injection

COMPONENT STRUCTURE:
- Import all necessary modules (CommonModule, FormsModule, ReactiveFormsModule, Material modules)
- Define interfaces for data models
- Include mock/sample data for demonstration
- Add proper error handling
- Include loading states where appropriate

STYLING:
- Use SCSS with BEM-like naming convention
- Make components responsive
- Use CSS variables for theming
- Include hover states and transitions

OUTPUT: Return ONLY the 3 code blocks. No explanations. No additional text."""
    
    def _get_angular_user_prompt(self, page: Dict, wireframe_html: str, project_context: str) -> str:
        """User prompt for Angular component generation with feature mapping"""
        
        # Build feature-specific requirements
        feature_context = ""
        related_features = page.get('related_features', [])
        if related_features:
            feature_context += "\nRELATED FEATURES (implement these):\n"
            for feature in related_features:
                feature_context += f"  - {feature}\n"
        
        # Build story-specific requirements
        story_context = ""
        related_stories = page.get('related_stories', [])
        if related_stories:
            story_context += "\nUSER STORIES (the component must support these):\n"
            for story in related_stories:
                story_context += f"  - {story}\n"
        
        # Build functionality requirements
        func_context = ""
        functionality = page.get('functionality', [])
        if functionality:
            func_context += "\nREQUIRED FUNCTIONALITY (implement as methods/properties):\n"
            for func in functionality:
                func_context += f"  - {func}\n"
        
        # Build UI element requirements
        ui_context = ""
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            ui_context += "\nREQUIRED UI ELEMENTS:\n"
            for element in ui_elements:
                ui_context += f"  - {element}\n"
        
        # Build data requirements
        data_context = ""
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            data_context += "\nDATA TO DISPLAY (create interfaces/types for these):\n"
            for data in data_displayed:
                data_context += f"  - {data}\n"
        
        return f"""Create an Angular component that implements this wireframe UI.

PAGE INFO:
- Name: {page.get('name', 'Page')}
- Type: {self.page_type}
- Description: {page.get('description', 'No description')}
{feature_context}{story_context}{func_context}{ui_context}{data_context}

PROJECT CONTEXT:
{project_context}

WIREFRAME HTML (for reference - recreate using Angular patterns):
{wireframe_html[:3000]}

IMPLEMENTATION REQUIREMENTS:
1. Create TypeScript interfaces for all data models mentioned
2. Implement methods for each functionality item
3. Use Angular Material components for the required UI elements
4. Include realistic mock data that matches the feature requirements
5. Add proper loading, error, and empty states
6. Make the component fully functional with the specified features

Generate a complete Angular 18+ standalone component with:
1. TypeScript component class with proper imports, interfaces, and logic
2. HTML template using Angular syntax (@if, @for, etc.)
3. SCSS styles that match the wireframe design

{self._get_page_type_specific_prompt()}"""
    
    def _get_page_type_specific_prompt(self) -> str:
        """Override in subclasses for page-type specific instructions"""
        return """Include appropriate Angular Material components and patterns for this page type."""
    
    def _parse_angular_response(self, response: str, component_name: str, selector_name: str) -> Dict[str, str]:
        """Parse the LLM response to extract TS, HTML, and SCSS code blocks"""
        import re
        
        typescript = ""
        html = ""
        scss = ""
        
        # Extract TypeScript block
        ts_match = re.search(r'```typescript\s*([\s\S]*?)```', response)
        if ts_match:
            typescript = ts_match.group(1).strip()
        
        # Extract HTML block
        html_match = re.search(r'```html\s*([\s\S]*?)```', response)
        if html_match:
            html = html_match.group(1).strip()
        
        # Extract SCSS block
        scss_match = re.search(r'```scss\s*([\s\S]*?)```', response)
        if scss_match:
            scss = scss_match.group(1).strip()
        
        # If parsing failed, use fallback
        if not typescript or not html:
            return self._get_fallback_angular_component(
                {"name": component_name}, 
                component_name, 
                selector_name
            )
        
        return {
            "typescript": typescript,
            "html": html,
            "scss": scss
        }
    
    def _get_fallback_angular_component(self, page: Dict, component_name: str, selector_name: str) -> Dict[str, str]:
        """Return fallback Angular component code when generation fails"""
        page_name = page.get('name', 'Page')
        
        typescript = f'''import {{ Component, OnInit, signal }} from '@angular/core';
import {{ CommonModule }} from '@angular/common';
import {{ MatCardModule }} from '@angular/material/card';
import {{ MatButtonModule }} from '@angular/material/button';
import {{ MatIconModule }} from '@angular/material/icon';

@Component({{
  selector: 'app-{selector_name}',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule, MatIconModule],
  templateUrl: './{selector_name}.component.html',
  styleUrls: ['./{selector_name}.component.scss']
}})
export class {component_name}Component implements OnInit {{
  pageTitle = signal('{page_name}');
  isLoading = signal(false);

  ngOnInit(): void {{
    this.loadData();
  }}

  async loadData(): Promise<void> {{
    this.isLoading.set(true);
    try {{
      // Load data here
    }} finally {{
      this.isLoading.set(false);
    }}
  }}
}}'''

        html = f'''<div class="{selector_name}-container">
  <header class="page-header">
    <h1>{{{{ pageTitle() }}}}</h1>
  </header>
  
  <main class="page-content">
    @if (isLoading()) {{
      <div class="loading-spinner">
        <mat-spinner></mat-spinner>
      </div>
    }} @else {{
      <mat-card>
        <mat-card-header>
          <mat-card-title>{page_name}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <p>Content goes here</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button color="primary">Action</button>
        </mat-card-actions>
      </mat-card>
    }}
  </main>
</div>'''

        scss = f'''.{selector_name}-container {{
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {{
    margin-bottom: 24px;
    
    h1 {{
      font-size: 24px;
      font-weight: 500;
      color: #333;
    }}
  }}

  .page-content {{
    .loading-spinner {{
      display: flex;
      justify-content: center;
      padding: 48px;
    }}

    mat-card {{
      margin-bottom: 16px;
    }}
  }}
}}'''

        return {
            "typescript": typescript,
            "html": html,
            "scss": scss
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
        # Build feature-specific requirements
        feature_context = ""
        related_features = page.get('related_features', [])
        if related_features:
            feature_context += "\n\nRELATED FEATURES (show UI for these):\n"
            for feature in related_features:
                feature_context += f"  - {feature}\n"
        
        # Build functionality requirements
        func_context = ""
        functionality = page.get('functionality', [])
        if functionality:
            func_context += "\n\nREQUIRED FUNCTIONALITY (include UI elements for):\n"
            for func in functionality:
                func_context += f"  - {func}\n"
        
        # Build UI element requirements
        ui_context = ""
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            ui_context += "\n\nREQUIRED UI ELEMENTS:\n"
            for element in ui_elements:
                ui_context += f"  - {element}\n"
        
        # Build data requirements
        data_context = ""
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            data_context += "\n\nDATA TO DISPLAY:\n"
            for data in data_displayed:
                data_context += f"  - {data}\n"
        
        return f"""Create the main content for a {self.page_type} page.

PAGE INFO:
- Name: {page.get('name', 'Page')}
- Description: {page.get('description', 'No description')}{feature_context}{func_context}{ui_context}{data_context}

PROJECT CONTEXT:
{project_context}

IMPORTANT: Generate a wireframe that specifically implements the features and functionality listed above.
Use realistic placeholder data that matches the feature requirements.

Generate a BEAUTIFUL, COMPLETE UI with:
- Professional layout with proper visual hierarchy
- All inline styles (no external CSS)
- Realistic placeholder data matching the features
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
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for a Dashboard page.

PAGE: {page.get('name', 'Dashboard')}
DESCRIPTION: {page.get('description', 'Main dashboard overview')}
{feature_context}

CONTEXT: {project_context}

Use the wireframe CSS classes provided (wf-card, wf-btn, wf-heading, wf-placeholder, grid-4, etc.)

RESPONSIVE DESIGN - Use these responsive patterns:
- Use grid-4 class for KPI cards (auto-wraps on smaller screens)
- Use grid-2 class for charts (auto-wraps to single column)
- Wrap tables in <div class="table-wrapper"> for horizontal scroll
- Avoid fixed pixel widths on containers

IMPORTANT: The KPIs, charts, and tables MUST reflect the features and functionality specified above.
Use realistic labels and data that match the project context.

Include these wireframe sections:
1. PAGE HEADER: Simple heading with placeholder date text
2. KPI CARDS ROW (class="grid-4"): 4 simple cards with:
   - Labels relevant to the features (e.g., for e-commerce: Orders, Revenue, Users, etc.)
   - Large number placeholder
   - Small change indicator text
3. CHARTS SECTION (class="grid-2"): 2 placeholder boxes for charts
   - Chart types relevant to the features
   - Use wf-placeholder class with descriptive chart title
   - Make them about 200px tall
4. RECENT ACTIVITY TABLE (wrapped in table-wrapper):
   - Columns relevant to the main features
   - 4-5 placeholder rows with realistic data

Keep it SIMPLE - grayscale, no colors, RESPONSIVE, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nDATA TO DISPLAY:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """DASHBOARD-SPECIFIC REQUIREMENTS:
- Create KPI card components with:
  - title, value, change percentage, icon inputs
  - Color coding for positive/negative changes
- Include chart placeholder components (ready for ng2-charts integration)
- Create a data table component with:
  - MatTableDataSource for data
  - MatSort for sorting
  - Column definitions
- Use signals for reactive KPI values
- Include a date range selector component
- Add refresh/reload functionality"""


class ListPageAgent(BasePageAgent):
    """Generates list/table pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "list"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for a List/Table page.

PAGE: {page.get('name', 'Items')}
DESCRIPTION: {page.get('description', 'Item listing page')}
{feature_context}

CONTEXT: {project_context}

Use the wireframe CSS classes provided (wf-card, wf-btn, wf-input, wf-heading, etc.)

RESPONSIVE DESIGN - Use these responsive patterns:
- Wrap filters in flex container with flex-wrap
- MUST wrap table in <div class="table-wrapper"> for horizontal scroll on mobile
- Use width: 100% on inputs
- Filters should stack on mobile

IMPORTANT: The table columns, filters, and data MUST reflect the features specified above.
Use column names and filter options that match the data type being listed.

Include these wireframe sections:
1. PAGE HEADER: Title and "Add New" button (wf-btn wf-btn-primary)
2. FILTERS BAR (wf-card, use class="flex gap-10" with flex-wrap): 
   - Search input (wf-input, style="max-width:300px") 
   - 2-3 filter dropdowns relevant to the data type
3. DATA TABLE (MUST be inside <div class="table-wrapper">):
   - Column headers matching the data fields from features
   - 5 placeholder data rows with realistic data
   - Action column with "Edit | Delete" text links
4. PAGINATION:
   - "Showing 1-10 of 50" text
   - Simple page number links

Keep it SIMPLE - grayscale, basic table, RESPONSIVE, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nDATA TO DISPLAY:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """LIST/TABLE-SPECIFIC REQUIREMENTS:
- Use MatTableModule with MatTableDataSource
- Implement MatSort for column sorting
- Include MatPaginator for pagination
- Add search/filter functionality:
  - debounced search input
  - filter by status/category dropdowns
- Create an interface for the list item data
- Include selection with MatCheckbox
- Add action buttons (edit, delete, view)
- Implement loading skeleton state
- Use @Output() for action events
- Include empty state handling"""


class DetailPageAgent(BasePageAgent):
    """Generates detail/view pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "detail"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for a Detail page.

PAGE: {page.get('name', 'Item Detail')}
DESCRIPTION: {page.get('description', 'Item detail view')}
{feature_context}

CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-heading, wf-placeholder, etc.)

IMPORTANT: The detail fields and sections MUST reflect the features and data specified above.
Show fields and information relevant to the item type.

Include:
1. BREADCRUMB: Simple text navigation path
2. PAGE HEADER: Back button, title, action buttons
3. MAIN INFO CARD: Image placeholder on left, key details on right
4. DETAILS SECTION: 2-column grid showing all relevant fields from the data specification
5. RELATED ITEMS: Section showing related data if applicable

Keep it SIMPLE - grayscale, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nDATA TO DISPLAY:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """DETAIL PAGE-SPECIFIC REQUIREMENTS:
- Create an interface for the detail item data
- Use @Input() for item ID or full item object
- Implement data loading with a service (mock data for now)
- Include MatTabGroup for organizing content sections
- Add image gallery/carousel placeholder
- Create detail field component for label-value pairs
- Include edit/delete action buttons with @Output() events
- Add breadcrumb navigation
- Implement related items section
- Handle loading and error states
- Include back navigation"""


class FormPageAgent(BasePageAgent):
    """Generates form pages (create/edit)"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "form"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for a Form page.

PAGE: {page.get('name', 'Create/Edit')}
DESCRIPTION: {page.get('description', 'Form for creating or editing')}
{feature_context}

CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-input, wf-label, etc.)

IMPORTANT: The form fields MUST match the data fields specified in the features above.
Include all required fields for the entity being created/edited.

Include:
1. PAGE HEADER: Title and Cancel/Save buttons
2. FORM CARD with sections:
   - Form fields matching the required data (wf-label + wf-input)
   - Group related fields in sections
   - 2-column layout for fields where appropriate
   - Text areas for long content
   - Dropdowns for selection fields
3. FOOTER: Cancel and Save buttons

Keep it SIMPLE - grayscale, basic form, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nDATA TO DISPLAY/COLLECT:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """FORM PAGE-SPECIFIC REQUIREMENTS:
- Use ReactiveFormsModule with FormGroup and FormControl
- Implement comprehensive form validation:
  - required fields
  - email validation
  - min/max length
  - pattern matching
- Show validation error messages with mat-error
- Include various field types:
  - MatFormField with MatInput
  - MatSelect for dropdowns
  - MatDatepicker for dates
  - MatCheckbox and MatRadioButton
  - textarea for long text
- Implement form sections with MatExpansionPanel or MatCard
- Add @Input() for edit mode (pass existing data)
- Include @Output() for form submission
- Add dirty state tracking and unsaved changes warning
- Include cancel/reset functionality
- Show loading state during submission"""


class SettingsPageAgent(BasePageAgent):
    """Generates settings/configuration pages"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "settings"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for a Settings page.

PAGE: {page.get('name', 'Settings')}
DESCRIPTION: {page.get('description', 'Settings and configuration')}
{feature_context}

CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-input, etc.)

IMPORTANT: The settings options MUST match the features and functionality specified above.
Include settings relevant to the application's features.

Include:
1. Settings navigation on left (simple list matching settings categories)
2. Settings content on right:
   - Section titles for each category
   - Toggle placeholders [On/Off] for boolean settings
   - Input fields for text/numeric settings
   - Dropdowns for selection settings
3. Save button at bottom

Keep it SIMPLE - grayscale, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED SETTINGS:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nSETTING CATEGORIES:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """SETTINGS PAGE-SPECIFIC REQUIREMENTS:
- Create a settings navigation component (sidebar or tabs)
- Organize settings into logical groups:
  - Profile settings
  - Notification preferences
  - Security settings
  - Display/Theme options
- Use MatSlideToggle for boolean settings
- Use MatSelect for option settings
- Include MatInput for text settings
- Implement settings as a FormGroup
- Add auto-save or explicit save button
- Show success/error feedback with MatSnackBar
- Include reset to defaults functionality
- Track which settings have been modified
- Use signal() for reactive settings state"""


class AuthPageAgent(BasePageAgent):
    """Generates authentication pages (login/register)"""
    
    def __init__(self, client):
        super().__init__(client)
        self.page_type = "auth"
    
    def _get_user_prompt(self, page: Dict, components: Dict, theme: Dict, project_context: str) -> str:
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        # Determine if this is login, register, or another auth type
        page_name = page.get('name', 'Login').lower()
        
        if 'register' in page_name or 'signup' in page_name or 'sign up' in page_name:
            auth_type = "registration"
            title = "Sign Up"
            fields = """
   - Full name input
   - Email input
   - Password input
   - Confirm password input
   - Terms checkbox
   - "Sign Up" button
   - "Already have an account? Sign In" link"""
        elif 'forgot' in page_name or 'reset' in page_name:
            auth_type = "password reset"
            title = "Reset Password"
            fields = """
   - Email input
   - "Send Reset Link" button
   - "Back to Sign In" link"""
        else:
            auth_type = "login"
            title = "Sign In"
            fields = """
   - Email input
   - Password input
   - "Remember me" checkbox
   - Login button
   - "Forgot password?" link
   - "Sign up" link"""
        
        return f"""Create a LOW-FIDELITY WIREFRAME for an Auth page ({auth_type}).

PAGE: {page.get('name', 'Login')}
DESCRIPTION: {page.get('description', f'User {auth_type} page')}
{feature_context}

This is a FULL PAGE (no sidebar/header).

IMPORTANT: If the features specify social login or other auth methods, include them.

Include:
1. Centered card with:
   - Logo placeholder
   - Title "{title}"
   {fields}
2. Optional social login buttons if applicable

Keep it SIMPLE - grayscale, basic form, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """AUTH PAGE-SPECIFIC REQUIREMENTS:
- Create both login and registration form variants
- Use ReactiveFormsModule for form handling
- Implement form validation:
  - Email format validation
  - Password strength validation
  - Password confirmation matching
- Include social login buttons (Google, GitHub, etc.)
- Add "Remember me" checkbox
- Include "Forgot password?" link/flow
- Show password visibility toggle
- Handle loading state during auth
- Display error messages for failed auth
- Include router navigation after success
- Support responsive layout (centered card)
- Add animations for form transitions"""
    
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
        # Build feature-specific requirements
        feature_context = self._build_feature_context(page)
        
        return f"""Create a LOW-FIDELITY WIREFRAME for: {page.get('name', 'Page')}

Description: {page.get('description', 'Generic page')}
{feature_context}

CONTEXT: {project_context}

Use wireframe CSS classes (wf-card, wf-btn, wf-heading, etc.)

IMPORTANT: The layout and content MUST reflect the features and functionality specified above.

Create a layout with:
- Page heading
- Content sections using wf-card that match the required functionality
- Placeholder areas for the specified UI elements
- Data display matching the requirements

Keep it SIMPLE - grayscale, sketch-like appearance."""
    
    def _build_feature_context(self, page: Dict) -> str:
        """Build feature context string for prompts"""
        parts = []
        
        related_features = page.get('related_features', [])
        if related_features:
            parts.append("\nRELATED FEATURES:")
            for f in related_features:
                parts.append(f"  - {f}")
        
        functionality = page.get('functionality', [])
        if functionality:
            parts.append("\nREQUIRED FUNCTIONALITY:")
            for f in functionality:
                parts.append(f"  - {f}")
        
        ui_elements = page.get('ui_elements', [])
        if ui_elements:
            parts.append("\nREQUIRED UI ELEMENTS:")
            for e in ui_elements:
                parts.append(f"  - {e}")
        
        data_displayed = page.get('data_displayed', [])
        if data_displayed:
            parts.append("\nDATA TO DISPLAY:")
            for d in data_displayed:
                parts.append(f"  - {d}")
        
        return "\n".join(parts)

    def _get_page_type_specific_prompt(self) -> str:
        return """GENERIC PAGE REQUIREMENTS:
- Create a flexible layout component
- Include common Angular Material components
- Add basic content sections
- Implement responsive design
- Include sample data and interactions"""
