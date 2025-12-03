"""
Wireframe Orchestrator
Coordinates all agents for parallel wireframe generation
"""

import asyncio
from typing import Dict, Any, List
from anthropic import Anthropic

from .planning_agent import PlanningAgent
from .design_system_agent import DesignSystemAgent
from .page_agents import PageAgentFactory


class WireframeOrchestrator:
    """
    Orchestrates the wireframe generation workflow:
    1. Planning Agent -> determines pages needed
    2. Design System Agent -> creates shared components
    3. Page Agents (parallel) -> generates each page
    """
    
    def __init__(self, client: Anthropic):
        self.client = client
        self.planning_agent = PlanningAgent(client)
        self.design_system_agent = DesignSystemAgent(client)
        
    async def generate_wireframes(
        self, 
        project_context: Dict[str, Any],
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Generate complete wireframe package
        
        Args:
            project_context: Dict with project_summary, features, hld_summary, api_summary
            progress_callback: Optional async callback for progress updates
            
        Returns:
            Dict with pages, shared_components, metadata
        """
        
        result = {
            "pages": [],
            "shared_components": {},
            "plan": {},
            "metadata": {
                "total_pages": 0,
                "generation_time": 0
            }
        }
        
        try:
            # STEP 1: Planning
            if progress_callback:
                await progress_callback("planning", "Analyzing project structure...")
            
            print("[Orchestrator] Step 1: Planning pages...")
            plan = await self.planning_agent.execute(project_context)
            result["plan"] = plan
            
            pages_to_generate = plan.get("pages", [])
            result["metadata"]["total_pages"] = len(pages_to_generate)
            
            print(f"[Orchestrator] Planned {len(pages_to_generate)} pages")
            
            # STEP 2: Generate shared components
            if progress_callback:
                await progress_callback("components", "Creating design system...")
            
            print("[Orchestrator] Step 2: Generating shared components...")
            components = await self.design_system_agent.execute({"plan": plan})
            result["shared_components"] = components
            
            # STEP 3: Generate pages in parallel
            if progress_callback:
                await progress_callback("pages", f"Generating {len(pages_to_generate)} pages...")
            
            print(f"[Orchestrator] Step 3: Generating {len(pages_to_generate)} pages in parallel...")
            
            # Create tasks for parallel execution
            tasks = []
            for page in pages_to_generate:
                task = self._generate_page(
                    page=page,
                    components=components,
                    theme=plan.get("theme", {}),
                    project_context=project_context.get("project_summary", "")
                )
                tasks.append(task)
            
            # Execute all page generations in parallel
            generated_pages = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, page_result in enumerate(generated_pages):
                if isinstance(page_result, Exception):
                    print(f"[Orchestrator] Page {i} failed: {page_result}")
                    # Add error placeholder
                    result["pages"].append({
                        "id": pages_to_generate[i].get("id", f"page-{i}"),
                        "name": pages_to_generate[i].get("name", f"Page {i}"),
                        "type": pages_to_generate[i].get("type", "generic"),
                        "html": self._get_error_page(str(page_result)),
                        "error": str(page_result)
                    })
                else:
                    result["pages"].append(page_result)
                    
                if progress_callback:
                    await progress_callback(
                        "page_complete", 
                        f"Completed {i + 1}/{len(pages_to_generate)} pages"
                    )
            
            if progress_callback:
                await progress_callback("complete", "All wireframes generated!")
            
            print(f"[Orchestrator] Complete! Generated {len(result['pages'])} pages")
            return result
            
        except Exception as e:
            print(f"[Orchestrator] Error: {str(e)}")
            raise
    
    async def _generate_page(
        self,
        page: Dict[str, Any],
        components: Dict[str, str],
        theme: Dict[str, str],
        project_context: str
    ) -> Dict[str, Any]:
        """Generate a single page using the appropriate agent"""
        
        page_type = page.get("type", "generic")
        agent = PageAgentFactory.create(page_type, self.client)
        
        context = {
            "page": page,
            "components": components,
            "theme": theme,
            "project_context": project_context
        }
        
        return await agent.execute(context)
    
    def _get_error_page(self, error: str) -> str:
        """Generate error page HTML"""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-200 min-h-screen flex items-center justify-center">
    <div class="text-center p-8">
        <div class="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
        </div>
        <h2 class="text-xl font-semibold text-white mb-2">Page Generation Failed</h2>
        <p class="text-slate-400 text-sm">{error[:200]}</p>
    </div>
</body>
</html>'''


async def generate_single_page(
    client: Anthropic,
    page_type: str,
    page_name: str,
    project_context: str,
    components: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    Utility function to generate a single page
    Useful for regenerating individual pages
    """
    
    if components is None:
        # Generate default components
        design_agent = DesignSystemAgent(client)
        components = await design_agent.execute({
            "plan": {
                "navigation": {"sidebar_items": []},
                "theme": {}
            }
        })
    
    agent = PageAgentFactory.create(page_type, client)
    
    return await agent.execute({
        "page": {
            "id": page_name.lower().replace(" ", "-"),
            "name": page_name,
            "type": page_type,
            "description": f"{page_name} page"
        },
        "components": components,
        "theme": {},
        "project_context": project_context
    })
