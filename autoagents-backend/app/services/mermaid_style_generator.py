"""Dynamic Mermaid diagram style generator based on domain/prompt analysis."""

import hashlib
import logging
import re
from typing import Dict, List, Literal, TypedDict

logger = logging.getLogger(__name__)

# Domain keyword mappings
DOMAIN_KEYWORDS = {
    "e-commerce": ["e-commerce", "ecommerce", "online store", "shopping", "retail", "marketplace", "cart", "checkout", "product catalog"],
    "healthcare": ["healthcare", "health", "medical", "hospital", "clinic", "patient", "doctor", "pharmacy", "diagnosis", "treatment"],
    "finance": ["finance", "banking", "financial", "bank", "payment", "transaction", "account", "investment", "wallet", "credit", "loan"],
    "education": ["education", "learning", "school", "university", "student", "course", "teacher", "academic", "curriculum", "training"],
    "technology": ["technology", "tech", "software", "application", "system", "platform", "api", "development"],
    "social": ["social", "community", "network", "chat", "messaging", "forum", "profile"],
    "entertainment": ["entertainment", "media", "video", "music", "streaming", "gaming", "content"],
    "logistics": ["logistics", "shipping", "delivery", "supply chain", "warehouse", "inventory", "transport"],
}

# Style configuration options
THEMES = ["default", "forest", "dark", "neutral", "base"]
NODE_SHAPES = ["round", "rect", "stadium", "circle", "diamond", "hexagon", "parallelogram"]
ARROW_STYLES = ["solid", "dotted", "thick"]
FONT_FAMILIES = ["Arial, sans-serif", "Georgia, serif", "Courier New, monospace", "Verdana, sans-serif", "Trebuchet MS, sans-serif"]
FONT_SIZES = ["14px", "16px", "18px", "20px"]

# Domain-specific color schemes
DOMAIN_COLORS = {
    "e-commerce": {
        "primary": "#FF6B6B",      # Coral red
        "secondary": "#4ECDC4",     # Teal
        "accent": "#FFE66D",        # Yellow
        "background": "#F7F7F7",
    },
    "healthcare": {
        "primary": "#5DADE2",       # Medical blue
        "secondary": "#58D68D",      # Health green
        "accent": "#F7DC6F",        # Light yellow
        "background": "#EBF5FB",
    },
    "finance": {
        "primary": "#1E8449",       # Banking green
        "secondary": "#2874A6",      # Trust blue
        "accent": "#F39C12",        # Gold
        "background": "#F8F9FA",
    },
    "education": {
        "primary": "#3498DB",       # Learning blue
        "secondary": "#9B59B6",     # Creative purple
        "accent": "#E74C3C",        # Alert red
        "background": "#ECF0F1",
    },
    "technology": {
        "primary": "#2C3E50",       # Tech dark blue
        "secondary": "#3498DB",     # Tech blue
        "accent": "#E74C3C",        # Tech red
        "background": "#ECF0F1",
    },
    "social": {
        "primary": "#4267B2",      # Social blue
        "secondary": "#1DA1F2",     # Twitter blue
        "accent": "#E1306C",        # Instagram pink
        "background": "#F5F5F5",
    },
    "entertainment": {
        "primary": "#E74C3C",       # Entertainment red
        "secondary": "#9B59B6",      # Creative purple
        "accent": "#F39C12",        # Orange
        "background": "#2C2C2C",
    },
    "logistics": {
        "primary": "#16A085",       # Logistics teal
        "secondary": "#F39C12",     # Orange
        "accent": "#E67E22",        # Dark orange
        "background": "#EAEDED",
    },
    "default": {
        "primary": "#3b82f6",       # Default blue
        "secondary": "#10b981",     # Default green
        "accent": "#f59e0b",        # Default orange
        "background": "#ffffff",
    },
}


class MermaidStyleConfig(TypedDict):
    """Type definition for Mermaid style configuration."""
    theme: str
    nodeShape: str
    primaryColor: str
    secondaryColor: str
    accentColor: str
    backgroundColor: str
    arrowStyle: str
    fontSize: str
    fontFamily: str
    domain: str


def extract_domain_keywords(prompt: str) -> List[str]:
    """Extract domain keywords from a prompt.
    
    Args:
        prompt: The user's original prompt text
        
    Returns:
        List of detected domain keywords
    """
    if not prompt:
        return []
    
    prompt_lower = prompt.lower()
    detected_domains = []
    
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                detected_domains.append(domain)
                break
    
    return detected_domains


def deterministic_hash(text: str, seed: int = 0) -> int:
    """Generate a deterministic hash from text.
    
    Args:
        text: Input text to hash
        seed: Optional seed for additional variation
        
    Returns:
        Integer hash value
    """
    combined = f"{text}{seed}".encode('utf-8')
    hash_obj = hashlib.sha256(combined)
    return int(hash_obj.hexdigest(), 16)


def select_from_hash(hash_value: int, options: List[str]) -> str:
    """Select an option from a list using hash value.
    
    Args:
        hash_value: Hash integer to use for selection
        options: List of options to choose from
        
    Returns:
        Selected option
    """
    if not options:
        return ""
    index = hash_value % len(options)
    return options[index]


def generate_style_from_prompt(prompt: str, project_id: str = "") -> MermaidStyleConfig:
    """Generate a consistent style configuration from a prompt.
    
    This function:
    1. Extracts domain keywords from the prompt
    2. Uses a deterministic hash to select style options
    3. Returns a consistent style configuration
    
    Args:
        prompt: The user's original prompt text
        project_id: Optional project ID for additional consistency
        
    Returns:
        MermaidStyleConfig dictionary with all style properties
    """
    # Extract domain
    domains = extract_domain_keywords(prompt)
    primary_domain = domains[0] if domains else "default"
    
    # Create a consistent hash seed from prompt + project_id
    hash_seed = f"{prompt}{project_id}".strip()
    base_hash = deterministic_hash(hash_seed)
    
    # Select theme based on hash
    theme = select_from_hash(base_hash, THEMES)
    
    # Select node shape
    node_shape = select_from_hash(base_hash + 1, NODE_SHAPES)
    
    # Select arrow style
    arrow_style = select_from_hash(base_hash + 2, ARROW_STYLES)
    
    # Select font family
    font_family = select_from_hash(base_hash + 3, FONT_FAMILIES)
    
    # Select font size
    font_size = select_from_hash(base_hash + 4, FONT_SIZES)
    
    # Get domain-specific colors
    domain_colors = DOMAIN_COLORS.get(primary_domain, DOMAIN_COLORS["default"])
    
    # Create style configuration
    style_config: MermaidStyleConfig = {
        "theme": theme,
        "nodeShape": node_shape,
        "primaryColor": domain_colors["primary"],
        "secondaryColor": domain_colors["secondary"],
        "accentColor": domain_colors["accent"],
        "backgroundColor": domain_colors["background"],
        "arrowStyle": arrow_style,
        "fontSize": font_size,
        "fontFamily": font_family,
        "domain": primary_domain,
    }
    
    logger.info(
        f"[mermaid_style] Generated style for domain '{primary_domain}' | "
        f"theme={theme} | shape={node_shape} | colors={domain_colors['primary']}"
    )
    
    return style_config


def inject_theme_directive(mermaid_source: str, style_config: MermaidStyleConfig) -> str:
    """Inject Mermaid theme directive using %%init%% syntax.
    
    Args:
        mermaid_source: Original Mermaid diagram source code
        style_config: Style configuration to apply
        
    Returns:
        Mermaid source code with theme directive injected
    """
    if not mermaid_source or not style_config:
        return mermaid_source
    
    # Check if init directive already exists
    if "%%{init:" in mermaid_source or "%%{ init:" in mermaid_source:
        logger.debug("[mermaid_style] Init directive already exists, skipping injection")
        return mermaid_source
    
    # Build init directive with theme and themeVariables
    theme_name = style_config.get("theme", "default")
    
    # Create themeVariables object
    theme_vars = {
        "primaryColor": style_config.get("primaryColor", "#3b82f6"),
        "primaryTextColor": "#fff",
        "primaryBorderColor": _darken_color(style_config.get("primaryColor", "#3b82f6"), 0.2),
        "lineColor": _get_line_color(style_config.get("arrowStyle", "solid"), style_config.get("primaryColor", "#3b82f6")),
        "secondaryColor": style_config.get("secondaryColor", "#10b981"),
        "tertiaryColor": style_config.get("accentColor", "#f59e0b"),
        "fontSize": style_config.get("fontSize", "16px"),
        "fontFamily": style_config.get("fontFamily", "Arial, sans-serif"),
    }
    
    # Format as JSON string for Mermaid (Mermaid uses single quotes)
    import json
    # Convert to JSON and replace double quotes with single quotes for Mermaid syntax
    theme_vars_json = json.dumps(theme_vars)
    theme_vars_str = theme_vars_json.replace('"', "'")
    
    # Create init directive - Mermaid format: %%{init: {'theme':'name', 'themeVariables':{...}}}%%
    init_directive = f"%%{{init: {{'theme':'{theme_name}', 'themeVariables':{theme_vars_str}}}}}%%"
    
    logger.debug(f"[mermaid_style] Init directive created | length={len(init_directive)} chars")
    
    logger.debug(f"[mermaid_style] Injecting theme directive: theme={theme_name}")
    
    # Prepend init directive to diagram
    return f"{init_directive}\n{mermaid_source}"


def _darken_color(hex_color: str, percent: float) -> str:
    """Darken a hex color by a percentage."""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, min(255, int(r * (1 - percent))))
        g = max(0, min(255, int(g * (1 - percent))))
        b = max(0, min(255, int(b * (1 - percent))))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#1e40af"  # Default dark blue


def _get_line_color(arrow_style: str, primary_color: str) -> str:
    """Get line color based on arrow style."""
    if arrow_style == "dotted":
        return _lighten_color(primary_color, 0.3)
    elif arrow_style == "thick":
        return primary_color
    else:
        return "#64748b"  # Default gray


def _lighten_color(hex_color: str, percent: float) -> str:
    """Lighten a hex color by a percentage."""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, min(255, int(r + (255 - r) * percent)))
        g = max(0, min(255, int(g + (255 - g) * percent)))
        b = max(0, min(255, int(b + (255 - b) * percent)))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#94a3b8"  # Default light gray


def apply_style_to_mermaid(mermaid_source: str, style_config: MermaidStyleConfig) -> str:
    """Apply style configuration to Mermaid diagram source code.
    
    This function injects Mermaid styling directives into the diagram code.
    
    Args:
        mermaid_source: Original Mermaid diagram source code
        style_config: Style configuration to apply
        
    Returns:
        Mermaid source code with styling applied
    """
    if not mermaid_source or not style_config:
        return mermaid_source
    
    logger.debug(f"[mermaid_style] Applying style to Mermaid diagram | length={len(mermaid_source)} chars")
    
    # Inject theme directive using %%init%% syntax
    styled_mermaid = inject_theme_directive(mermaid_source, style_config)
    
    # Add classDef for node styling (only for diagram types that support it)
    # classDef is only supported for: flowchart, graph
    # NOT supported for: classDiagram, erDiagram, sequenceDiagram, stateDiagram
    lines = styled_mermaid.split('\n')
    detected_diagram_type = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("flowchart") or stripped.startswith("graph "):
            detected_diagram_type = "flowchart"
            break
        elif stripped.startswith("classDiagram"):
            detected_diagram_type = "classDiagram"
            break
        elif stripped.startswith("erDiagram") or stripped.startswith("entityRelationshipDiagram"):
            detected_diagram_type = "erDiagram"
            break
        elif stripped.startswith("sequenceDiagram"):
            detected_diagram_type = "sequenceDiagram"
            break
        elif stripped.startswith("stateDiagram"):
            detected_diagram_type = "stateDiagram"
            break
    
    supports_classdef = detected_diagram_type and detected_diagram_type in ["flowchart", "graph"]
    
    # Only add classDef if diagram type supports it and it's not already present
    if supports_classdef and "classDef" not in styled_mermaid:
        style_lines = []
        style_lines.append(
            f"classDef primaryNode fill:{style_config['primaryColor']},stroke:{style_config['primaryColor']},stroke-width:2px,color:#fff"
        )
        style_lines.append(
            f"classDef secondaryNode fill:{style_config['secondaryColor']},stroke:{style_config['secondaryColor']},stroke-width:2px,color:#fff"
        )
        style_lines.append(
            f"classDef accentNode fill:{style_config['accentColor']},stroke:{style_config['accentColor']},stroke-width:2px,color:#fff"
        )
        
        # Insert classDef after init directive or at the beginning
        if "%%{init:" in styled_mermaid:
            init_line_idx = next((i for i, line in enumerate(lines) if "%%{init:" in line), 0)
            lines.insert(init_line_idx + 1, '')
            lines.insert(init_line_idx + 2, '\n'.join(style_lines))
            styled_mermaid = '\n'.join(lines)
        else:
            styled_mermaid = '\n'.join(style_lines) + '\n' + styled_mermaid
    elif detected_diagram_type and not supports_classdef:
        logger.debug(f"[mermaid_style] Skipping classDef for {detected_diagram_type} diagram type (not supported)")
    
    logger.debug(f"[mermaid_style] Style applied successfully | final_length={len(styled_mermaid)} chars")
    return styled_mermaid

