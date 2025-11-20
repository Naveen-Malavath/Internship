"""
Practical code examples for integrating the styling system into Agent 3 workflow.

These are ready-to-use code snippets that can be integrated into your existing codebase.
"""

# ============================================================================
# 1. WHERE TO CALL THE STYLE GENERATOR IN AGENT PIPELINE
# ============================================================================

# File: app/services/agent3.py
# Location: Agent3Service.generate_mermaid() method

async def generate_mermaid_with_styling(
    self,
    project_title: str,
    features: List[Dict],
    stories: List[Dict],
    diagram_type: str = "hld",
    original_prompt: str = "",
    project_id: str = "",
) -> str:
    """Generate Mermaid diagram with integrated styling system."""
    import logging
    from .style_config_generator import StyleConfigGenerator
    from .diagram_complexity import get_diagram_type_guidance
    from .node_shape_selector import NodeShapeSelector
    
    logger = logging.getLogger(__name__)
    logger.info(f"[agent3] Starting styled Mermaid generation | type={diagram_type} | prompt_length={len(original_prompt)}")
    
    # ============================================
    # STEP 1: Generate style configuration FIRST
    # ============================================
    logger.debug("[agent3] STEP 1: Generating style configuration from prompt")
    style_generator = StyleConfigGenerator(original_prompt, project_id)
    full_config = style_generator.generate_full_config(features, stories)
    
    # Extract style components
    style_config_dict = {
        "theme": full_config["theme"],
        "nodeShape": "rect",
        "primaryColor": full_config["colors"]["primary"],
        "secondaryColor": full_config["colors"]["secondary"],
        "accentColor": full_config["colors"]["tertiary"],
        "domain": full_config["domain"],
    }
    complexity_info = full_config["complexity"]
    init_directive = full_config["init_directive"]
    
    logger.info(
        f"[agent3] Style config generated | domain={full_config['domain']} | "
        f"theme={full_config['theme']} | primaryColor={full_config['colors']['primary']}"
    )
    
    # ============================================
    # STEP 2: Build prompts with style guidance
    # ============================================
    logger.debug("[agent3] STEP 2: Building prompts with style and complexity guidance")
    
    # Include original prompt context
    prompt_context = ""
    if original_prompt and original_prompt.strip():
        prompt_context = (
            f"\n\n=== ORIGINAL CUSTOMER REQUIREMENTS ===\n"
            f"{original_prompt.strip()}\n"
            f"=== END REQUIREMENTS ===\n\n"
        )
    
    # Initialize shape selector
    shape_selector = NodeShapeSelector(
        complexity_score=complexity_info["complexity_score"],
        prompt=original_prompt
    )
    shape_instructions = shape_selector.build_shape_instructions(complexity_info)
    
    # Get diagram type guidance
    diagram_guidance = get_diagram_type_guidance(diagram_type, complexity_info)
    
    # Build style guidance
    style_guidance = f"""
STYLE REQUIREMENTS:
- Theme: {style_config_dict['theme']}
- Primary Color: {style_config_dict['primaryColor']}
- Secondary Color: {style_config_dict['secondaryColor']}
- Accent Color: {style_config_dict['accentColor']}
- Domain: {style_config_dict['domain']}

Note: Style will be automatically injected via %%init%% directive. Focus on diagram structure and content.
"""
    
    # Build user prompt (example for HLD)
    user_prompt = (
        f"Project: {project_title or 'Untitled Project'}\n"
        f"{prompt_context}"
        f"Features: {len(features)}\n"
        f"Stories: {len(stories)}\n\n"
        f"{diagram_guidance}\n"
        f"{shape_instructions}\n"
        f"{style_guidance}\n"
        "Generate a Mermaid diagram. Output ONLY valid Mermaid code, no explanations."
    )
    
    # ============================================
    # STEP 3: Call Claude API
    # ============================================
    # ... (your existing API call code) ...
    
    # ============================================
    # STEP 4: Extract and clean Mermaid code
    # ============================================
    # ... (your existing extraction code) ...
    
    # ============================================
    # STEP 5: Apply style via %%init%% directive
    # ============================================
    logger.debug("[agent3] STEP 5: Applying style configuration to Mermaid diagram")
    
    # Remove any existing init directive
    if "%%{init:" in mermaid or "%%{ init:" in mermaid:
        lines = mermaid.split("\n")
        mermaid = "\n".join([line for line in lines if "%%{init:" not in line and "%%{ init:" not in line])
        mermaid = mermaid.strip()
    
    # Prepend init directive
    styled_mermaid = f"{init_directive}\n{mermaid}"
    
    logger.info(f"[agent3] Styled diagram generated | length={len(styled_mermaid)} chars")
    return styled_mermaid


# ============================================================================
# 2. PASSING ORIGINAL PROMPT THROUGH AGENT PIPELINE
# ============================================================================

# File: app/services/agent2.py
# Modify generate_stories_for_project() to pass prompt

async def generate_stories_for_project_with_prompt(project_id: str, db):
    """Generate stories - retrieve and pass original prompt."""
    from bson import ObjectId
    from fastapi import HTTPException
    
    # Get project to retrieve original prompt
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Extract original prompt
    project_prompt = project.get("prompt") or project.get("description") or ""
    logger.info(f"[agent2] Retrieved original prompt | length={len(project_prompt)} chars")
    
    # Get features
    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    
    if not features:
        raise HTTPException(status_code=400, detail="No features found. Run Agent-1 first.")
    
    # Convert features to expected format
    feature_list = []
    for feature in features:
        feature_dict = {
            "id": str(feature.get("_id", "")),
            "title": feature.get("feature_text") or feature.get("title") or "Feature",
            "description": feature.get("description") or feature.get("feature_text") or "",
        }
        feature_list.append(feature_dict)
    
    # Pass original prompt to Agent2Service
    agent2_service = Agent2Service()
    generated_stories = await agent2_service.generate_stories(
        feature_list,
        original_prompt=project_prompt  # ← Pass prompt here
    )
    
    # ... rest of story persistence code ...
    return generated_stories


# File: app/services/agent3.py
# Modify generate_designs_for_project() to retrieve and use prompt

async def generate_designs_for_project_with_prompt(project_id: str, db):
    """Generate designs - retrieve and use original prompt for styling."""
    from bson import ObjectId
    from fastapi import HTTPException
    from .style_config_generator import StyleConfigGenerator
    
    # Get project to retrieve original prompt
    try:
        object_id = ObjectId(project_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid project ID") from exc
    
    project = await db["projects"].find_one({"_id": object_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Extract original prompt
    project_title = project.get("title") or "Untitled Project"
    project_prompt = project.get("prompt") or project.get("description") or ""
    
    logger.info(
        f"[agent3] Retrieved project context | title={project_title} | "
        f"prompt_length={len(project_prompt)}"
    )
    
    # Get features and stories
    features_cursor = db["features"].find({"project_id": project_id}).sort("order_index", 1)
    features = await features_cursor.to_list(length=None)
    
    stories_cursor = db["stories"].find({"project_id": project_id}).sort("created_at", 1)
    stories = await stories_cursor.to_list(length=None)
    
    # ============================================
    # Generate style configuration from prompt
    # ============================================
    logger.info(f"[agent3] Generating style configuration from prompt")
    style_generator = StyleConfigGenerator(project_prompt, project_id)
    full_config = style_generator.generate_full_config(features, stories)
    
    # Extract style config for storage
    style_config = {
        "domain": full_config["domain"],
        "theme": full_config["theme"],
        "primaryColor": full_config["colors"]["primary"],
        "secondaryColor": full_config["colors"]["secondary"],
        "accentColor": full_config["colors"]["tertiary"],
        "complexity": full_config["complexity"],
        "init_directive": full_config["init_directive"],
    }
    
    # Use project_prompt in diagram generation prompts
    # ... (your existing diagram generation code using project_prompt) ...
    
    # Store style config with designs
    document = {
        "project_id": project_id,
        "hld_mermaid": hld_mermaid,
        "lld_mermaid": lld_mermaid,
        "dbd_mermaid": dbd_mermaid,
        "style_config": style_config,  # ← Store style config
        "created_at": datetime.utcnow(),
    }
    
    await db["designs"].insert_one(document)
    return document


# ============================================================================
# 3. CACHING STYLE DECISIONS PER PROJECT
# ============================================================================

# File: app/services/style_cache.py (NEW)
# Create this new file for style caching

import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId

logger = logging.getLogger(__name__)


def hash_prompt(prompt: str) -> str:
    """Generate deterministic hash for prompt to detect changes."""
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()


async def get_cached_style_config(project_id: str, prompt: str, db) -> Optional[Dict]:
    """Retrieve cached style configuration for a project."""
    prompt_hash = hash_prompt(prompt)
    
    # Check project document first (Option 1)
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    if project:
        cached_style = project.get("style_config")
        if cached_style and cached_style.get("prompt_hash") == prompt_hash:
            logger.info(f"[style_cache] Cache hit in project document for {project_id}")
            return cached_style.get("style_config")
    
    # Check style_cache collection (Option 2)
    cache_doc = await db["style_cache"].find_one({
        "project_id": project_id,
        "prompt_hash": prompt_hash,
    })
    
    if cache_doc:
        logger.info(f"[style_cache] Cache hit in style_cache collection for {project_id}")
        return cache_doc.get("style_config")
    
    logger.info(f"[style_cache] Cache miss for project {project_id}")
    return None


async def cache_style_config(
    project_id: str, 
    prompt: str, 
    style_config: Dict, 
    db,
    store_in_project: bool = True
):
    """Cache style configuration for a project."""
    prompt_hash = hash_prompt(prompt)
    
    cache_data = {
        "prompt_hash": prompt_hash,
        "style_config": style_config,
        "generated_at": datetime.utcnow(),
    }
    
    # Option 1: Store in project document
    if store_in_project:
        await db["projects"].update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"style_config": cache_data}}
        )
        logger.info(f"[style_cache] Cached style in project document for {project_id}")
    
    # Option 2: Store in separate collection
    cache_doc = {
        "project_id": project_id,
        "prompt_hash": prompt_hash,
        "style_config": style_config,
        "created_at": datetime.utcnow(),
    }
    
    await db["style_cache"].update_one(
        {"project_id": project_id, "prompt_hash": prompt_hash},
        {"$set": cache_doc},
        upsert=True
    )
    
    logger.info(f"[style_cache] Cached style in style_cache collection for {project_id}")


# Usage in Agent 3:
async def generate_designs_with_caching(project_id: str, db):
    """Generate designs with style caching."""
    from .style_cache import get_cached_style_config, cache_style_config
    from .style_config_generator import StyleConfigGenerator
    
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    project_prompt = project.get("prompt") or ""
    
    # Try to get cached style
    cached_style = await get_cached_style_config(project_id, project_prompt, db)
    
    if cached_style:
        logger.info(f"[agent3] Using cached style config for project {project_id}")
        full_config = cached_style
    else:
        # Generate new style
        logger.info(f"[agent3] Generating new style config for project {project_id}")
        style_generator = StyleConfigGenerator(project_prompt, project_id)
        full_config = style_generator.generate_full_config(features, stories)
        
        # Cache it
        await cache_style_config(project_id, project_prompt, full_config, db)
    
    # Use full_config for diagram generation
    # ... rest of implementation ...


# ============================================================================
# 4. COMPLETE MERMAID OUTPUT WITH CUSTOM STYLING
# ============================================================================

# Example: Complete styled Mermaid diagram output

EXAMPLE_STYLED_MERMAID = """
%%{init: {'theme':'forest', 'themeVariables':{'primaryColor':'#10B981', 'primaryTextColor':'#FFFFFF', 'primaryBorderColor':'#059669', 'lineColor':'#34D399', 'secondaryColor':'#F9FAFB', 'tertiaryColor':'#E5E7EB'}}}%%
flowchart LR
    subgraph Frontend["Frontend Layer"]
        UI[Patient Portal]
        Dashboard[Dashboard]
    end
    
    subgraph Backend["Backend Services"]
        AuthService[Authentication Service]
        PatientService[Patient Management Service]
        AppointmentService[Appointment Service]
        RecordService[Medical Records Service]
    end
    
    subgraph Data["Data Layer"]
        PatientDB[(Patient Database)]
        AppointmentDB[(Appointment Database)]
        RecordDB[(Medical Records Database)]
    end
    
    UI --> AuthService
    Dashboard --> PatientService
    PatientService --> PatientDB
    AppointmentService --> AppointmentDB
    RecordService --> RecordDB
    AuthService --> PatientService
    PatientService --> AppointmentService
    PatientService --> RecordService
    
    classDef primaryNode fill:#10B981,stroke:#059669,stroke-width:2px,color:#FFFFFF
    classDef secondaryNode fill:#F9FAFB,stroke:#059669,stroke-width:1px,color:#000000
    classDef accentNode fill:#E5E7EB,stroke:#059669,stroke-width:1px,color:#000000
    
    class AuthService,PatientService,AppointmentService,RecordService primaryNode
    class UI,Dashboard secondaryNode
    class PatientDB,AppointmentDB,RecordDB accentNode
"""


# Function to generate complete styled output
def generate_complete_styled_mermaid(
    mermaid_diagram: str,
    style_config: Dict,
    diagram_type: str = "hld"
) -> str:
    """Generate complete styled Mermaid output with init directive and classDef."""
    from .style_config_generator import StyleConfigGenerator
    
    # Get init directive from style config
    init_directive = style_config.get("init_directive", "")
    if not init_directive:
        # Generate if not provided
        generator = StyleConfigGenerator(style_config.get("prompt", ""), "")
        init_directive = generator.generate_init_directive(
            domain=style_config.get("domain"),
            theme=style_config.get("theme")
        )
    
    # Remove any existing init directive
    if "%%{init:" in mermaid_diagram:
        lines = mermaid_diagram.split("\n")
        mermaid_diagram = "\n".join([l for l in lines if "%%{init:" not in l])
        mermaid_diagram = mermaid_diagram.strip()
    
    # Prepend init directive
    styled = f"{init_directive}\n{mermaid_diagram}"
    
    # Add classDef for flowchart diagrams
    if diagram_type in ["hld", "lld"] and "flowchart" in mermaid_diagram.lower():
        if "classDef" not in styled:
            class_defs = [
                f"classDef primaryNode fill:{style_config['primaryColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:2px,color:#FFFFFF",
                f"classDef secondaryNode fill:{style_config['secondaryColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:1px,color:#000000",
                f"classDef accentNode fill:{style_config['accentColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:1px,color:#000000",
            ]
            
            # Insert classDef after init directive
            lines = styled.split("\n")
            init_line_idx = next((i for i, line in enumerate(lines) if "%%{init:" in line), 0)
            lines.insert(init_line_idx + 1, "")
            lines.insert(init_line_idx + 2, "\n".join(class_defs))
            styled = "\n".join(lines)
    
    return styled


# ============================================================================
# 5. MULTIPLE DIAGRAM TYPES WITH CONSISTENT STYLES
# ============================================================================

# Function to apply consistent style to all diagram types
def apply_consistent_style_to_all_diagrams(
    hld_mermaid: str,
    lld_mermaid: str,
    dbd_mermaid: str,
    style_config: Dict
) -> Dict[str, str]:
    """Apply consistent style to HLD, LLD, and DBD diagrams."""
    
    # All diagrams use the same init directive
    init_directive = style_config.get("init_directive", "")
    
    def apply_style(mermaid: str, diagram_type: str) -> str:
        """Apply style to a single diagram."""
        # Remove existing init directive
        if "%%{init:" in mermaid:
            lines = mermaid.split("\n")
            mermaid = "\n".join([l for l in lines if "%%{init:" not in l])
            mermaid = mermaid.strip()
        
        # Prepend init directive
        styled = f"{init_directive}\n{mermaid}"
        
        # Add diagram-type-specific styling
        if diagram_type == "hld" and "flowchart" in mermaid.lower():
            # Add classDef for HLD
            if "classDef" not in styled:
                class_defs = [
                    f"classDef primaryNode fill:{style_config['primaryColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:2px,color:#FFFFFF",
                    f"classDef secondaryNode fill:{style_config['secondaryColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:1px",
                ]
                lines = styled.split("\n")
                init_line_idx = next((i for i, line in enumerate(lines) if "%%{init:" in line), 0)
                lines.insert(init_line_idx + 1, "")
                lines.insert(init_line_idx + 2, "\n".join(class_defs))
                styled = "\n".join(lines)
        
        elif diagram_type == "lld" and "classDiagram" in mermaid:
            # Add classDef for LLD
            if "classDef" not in styled:
                class_def = f"classDef primaryClass fill:{style_config['primaryColor']},stroke:{style_config.get('primaryBorderColor', style_config['primaryColor'])},stroke-width:2px,color:#FFFFFF"
                lines = styled.split("\n")
                init_line_idx = next((i for i, line in enumerate(lines) if "%%{init:" in line), 0)
                lines.insert(init_line_idx + 1, "")
                lines.insert(init_line_idx + 2, class_def)
                styled = "\n".join(lines)
        
        # DBD (erDiagram) uses theme variables automatically, no additional styling needed
        
        return styled
    
    return {
        "hld_mermaid": apply_style(hld_mermaid, "hld"),
        "lld_mermaid": apply_style(lld_mermaid, "lld"),
        "dbd_mermaid": apply_style(dbd_mermaid, "database"),
    }


# Usage in generate_designs_for_project:
async def generate_all_diagrams_with_consistent_style(project_id: str, db):
    """Generate HLD, LLD, DBD with consistent styling."""
    from .style_config_generator import StyleConfigGenerator
    
    project = await db["projects"].find_one({"_id": ObjectId(project_id)})
    project_prompt = project.get("prompt") or ""
    
    # Generate style configuration ONCE (shared across all diagrams)
    style_generator = StyleConfigGenerator(project_prompt, project_id)
    full_config = style_generator.generate_full_config(features, stories)
    
    # Extract style config
    style_config = {
        "domain": full_config["domain"],
        "theme": full_config["theme"],
        "primaryColor": full_config["colors"]["primary"],
        "secondaryColor": full_config["colors"]["secondary"],
        "accentColor": full_config["colors"]["tertiary"],
        "primaryBorderColor": full_config["colors"].get("primaryBorder", full_config["colors"]["primary"]),
        "init_directive": full_config["init_directive"],
    }
    
    # Generate all three diagrams (your existing API call)
    # ... (hld_raw, lld_raw, dbd_raw from Claude API) ...
    
    # Apply consistent style to all diagrams
    styled_diagrams = apply_consistent_style_to_all_diagrams(
        hld_raw,
        lld_raw,
        dbd_raw,
        style_config
    )
    
    # Store with style config
    document = {
        "project_id": project_id,
        "hld_mermaid": styled_diagrams["hld_mermaid"],
        "lld_mermaid": styled_diagrams["lld_mermaid"],
        "dbd_mermaid": styled_diagrams["dbd_mermaid"],
        "style_config": style_config,  # Store for reference
        "created_at": datetime.utcnow(),
    }
    
    await db["designs"].insert_one(document)
    return document

