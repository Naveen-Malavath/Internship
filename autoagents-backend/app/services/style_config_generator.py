"""StyleConfigGenerator class for generating Mermaid diagram styles from customer prompts."""

import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class StyleConfigGenerator:
    """Generates Mermaid style configurations based on customer prompts and domain analysis."""
    
    # Enhanced domain keyword mappings with specific indicators
    DOMAIN_KEYWORDS = {
        "e-commerce": [
            "shop", "shopping", "store", "e-commerce", "ecommerce", "online store", 
            "retail", "marketplace", "cart", "checkout", "product", "catalog", 
            "purchase", "buy", "sell", "merchant", "vendor"
        ],
        "healthcare": [
            "hospital", "clinic", "healthcare", "health", "medical", "patient", 
            "doctor", "physician", "nurse", "pharmacy", "diagnosis", "treatment", 
            "appointment", "prescription", "health record", "medical record"
        ],
        "finance": [
            "bank", "banking", "finance", "financial", "payment", "transaction", 
            "account", "investment", "wallet", "credit", "loan", "mortgage", 
            "trading", "stock", "portfolio", "budget", "expense", "revenue"
        ],
        "education": [
            "school", "university", "college", "education", "learning", "student", 
            "teacher", "professor", "course", "curriculum", "academic", "training", 
            "lesson", "assignment", "grade", "exam", "certificate"
        ],
        "tech-ai": [
            "ai", "artificial intelligence", "machine learning", "ml", "iot", 
            "internet of things", "technology", "tech", "software", "application", 
            "system", "platform", "api", "development", "algorithm", "neural", 
            "deep learning", "data science", "analytics", "automation"
        ],
        "logistics": [
            "logistics", "shipping", "delivery", "supply chain", "warehouse", 
            "inventory", "transport", "freight", "distribution", "fulfillment"
        ],
        "social": [
            "social", "community", "network", "chat", "messaging", "forum", 
            "profile", "social media", "connect", "share", "follow"
        ],
    }
    
    # Domain-specific color palettes as requested
    DOMAIN_COLOR_PALETTES = {
        "e-commerce": {
            "primary": "#2563EB",      # Blue
            "primaryText": "#FFFFFF",
            "primaryBorder": "#1E40AF", # Darker blue
            "lineColor": "#3B82F6",     # Light blue
            "secondary": "#F97316",     # Orange
            "tertiary": "#FB923C",       # Light orange
        },
        "healthcare": {
            "primary": "#10B981",       # Green
            "primaryText": "#FFFFFF",
            "primaryBorder": "#059669", # Darker green
            "lineColor": "#34D399",     # Light green
            "secondary": "#F9FAFB",     # White
            "tertiary": "#E5E7EB",      # Light gray
        },
        "finance": {
            "primary": "#1E3A8A",       # Navy
            "primaryText": "#FFFFFF",
            "primaryBorder": "#1E40AF", # Darker navy
            "lineColor": "#3B82F6",    # Blue
            "secondary": "#F59E0B",     # Gold
            "tertiary": "#FBBF24",      # Light gold
        },
        "education": {
            "primary": "#7C3AED",       # Purple
            "primaryText": "#FFFFFF",
            "primaryBorder": "#6D28D9", # Darker purple
            "lineColor": "#A78BFA",     # Light purple
            "secondary": "#FCD34D",     # Yellow
            "tertiary": "#FDE047",      # Light yellow
        },
        "tech-ai": {
            "primary": "#06B6D4",       # Cyan
            "primaryText": "#FFFFFF",
            "primaryBorder": "#0891B2", # Darker cyan
            "lineColor": "#22D3EE",     # Light cyan
            "secondary": "#374151",     # Dark gray
            "tertiary": "#4B5563",      # Medium gray
        },
        "logistics": {
            "primary": "#16A085",       # Teal
            "primaryText": "#FFFFFF",
            "primaryBorder": "#138D75", # Darker teal
            "lineColor": "#48C9B0",    # Light teal
            "secondary": "#F39C12",     # Orange
            "tertiary": "#F7DC6F",      # Light orange
        },
        "social": {
            "primary": "#4267B2",       # Social blue
            "primaryText": "#FFFFFF",
            "primaryBorder": "#365899", # Darker blue
            "lineColor": "#5890FF",     # Light blue
            "secondary": "#1DA1F2",     # Twitter blue
            "tertiary": "#E1306C",      # Instagram pink
        },
        "default": {
            "primary": "#3B82F6",       # Default blue
            "primaryText": "#FFFFFF",
            "primaryBorder": "#2563EB", # Darker blue
            "lineColor": "#60A5FA",     # Light blue
            "secondary": "#10B981",      # Green
            "tertiary": "#F59E0B",       # Orange
        },
    }
    
    # Theme options
    THEMES = ["base", "default", "forest", "dark", "neutral"]
    
    def __init__(self, prompt: str, project_id: str = ""):
        """Initialize StyleConfigGenerator with customer prompt.
        
        Args:
            prompt: Customer prompt text
            project_id: Optional project ID for consistency
        """
        self.prompt = prompt or ""
        self.project_id = project_id or ""
        self.prompt_lower = self.prompt.lower() if self.prompt else ""
        
        logger.debug(f"[StyleConfigGenerator] Initialized | prompt_length={len(self.prompt)} | project_id={self.project_id}")
    
    def extract_domain(self) -> Tuple[str, List[str]]:
        """Extract domain from prompt using keyword matching.
        
        Returns:
            Tuple of (primary_domain, all_detected_domains)
        """
        if not self.prompt:
            logger.debug("[StyleConfigGenerator] No prompt provided, using default domain")
            return "default", []
        
        detected_domains = []
        domain_scores = {}
        
        # Score each domain based on keyword matches
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                if keyword in self.prompt_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                detected_domains.append(domain)
                domain_scores[domain] = {
                    "score": score,
                    "keywords": matched_keywords
                }
        
        # Select domain with highest score
        if domain_scores:
            primary_domain = max(domain_scores.items(), key=lambda x: x[1]["score"])[0]
            logger.info(
                f"[StyleConfigGenerator] Domain extracted | primary={primary_domain} | "
                f"score={domain_scores[primary_domain]['score']} | "
                f"keywords={domain_scores[primary_domain]['keywords'][:3]}"
            )
            return primary_domain, detected_domains
        
        logger.debug("[StyleConfigGenerator] No domain keywords found, using default")
        return "default", []
    
    def _deterministic_hash(self, seed: int = 0) -> int:
        """Generate deterministic hash from prompt and project_id.
        
        Args:
            seed: Optional seed for variation
            
        Returns:
            Integer hash value
        """
        combined = f"{self.prompt}{self.project_id}{seed}".encode('utf-8')
        hash_obj = hashlib.sha256(combined)
        return int(hash_obj.hexdigest(), 16)
    
    def _select_theme(self) -> str:
        """Select theme based on deterministic hash.
        
        Returns:
            Theme name
        """
        hash_value = self._deterministic_hash(0)
        theme = self.THEMES[hash_value % len(self.THEMES)]
        logger.debug(f"[StyleConfigGenerator] Theme selected | theme={theme}")
        return theme
    
    def get_color_palette(self, domain: str) -> Dict[str, str]:
        """Get color palette for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Dictionary of color values
        """
        palette = self.DOMAIN_COLOR_PALETTES.get(domain, self.DOMAIN_COLOR_PALETTES["default"])
        logger.debug(f"[StyleConfigGenerator] Color palette retrieved | domain={domain} | primary={palette['primary']}")
        return palette
    
    def analyze_complexity(self, features: Optional[List] = None, stories: Optional[List] = None) -> Dict:
        """Analyze architecture complexity to determine diagram type.
        
        Args:
            features: Optional list of features
            stories: Optional list of stories
            
        Returns:
            Dictionary with complexity metrics and recommended diagram type
        """
        num_features = len(features) if features else 0
        num_stories = len(stories) if stories else 0
        
        # Analyze prompt for complexity indicators
        state_keywords = ["state", "status", "workflow", "process", "stage", "phase", "transition"]
        has_state = any(kw in self.prompt_lower for kw in state_keywords)
        
        data_flow_keywords = ["data flow", "pipeline", "stream", "transform", "aggregate", "batch"]
        has_data_flow = any(kw in self.prompt_lower for kw in data_flow_keywords)
        
        workflow_keywords = ["workflow", "sequence", "pipeline", "orchestration", "multi-step"]
        has_workflow = any(kw in self.prompt_lower for kw in workflow_keywords)
        
        # Calculate complexity score
        complexity_score = (num_features * 2) + (num_stories * 1)
        if has_state:
            complexity_score += 10
        if has_data_flow:
            complexity_score += 8
        if has_workflow:
            complexity_score += 5
        
        # Determine diagram type
        if has_state and complexity_score > 15:
            recommended_type = "stateDiagram-v2"
            reason = "State-heavy system detected"
        elif has_data_flow and complexity_score > 12:
            recommended_type = "graph TB"
            reason = "Data flow system detected"
        elif has_workflow or complexity_score > 10:
            recommended_type = "flowchart LR"
            reason = "Complex workflow detected"
        else:
            recommended_type = "flowchart TD"
            reason = "Simple system"
        
        result = {
            "complexity_score": complexity_score,
            "num_features": num_features,
            "num_stories": num_stories,
            "has_state_indicators": has_state,
            "has_data_flow": has_data_flow,
            "has_workflow": has_workflow,
            "recommended_type": recommended_type,
            "reason": reason,
        }
        
        logger.info(
            f"[StyleConfigGenerator] Complexity analyzed | score={complexity_score} | "
            f"type={recommended_type} | reason={reason}"
        )
        
        return result
    
    def generate_init_directive(self, domain: Optional[str] = None, theme: Optional[str] = None) -> str:
        """Generate Mermaid %%init%% configuration directive.
        
        Args:
            domain: Optional domain override
            theme: Optional theme override
            
        Returns:
            Mermaid %%init%% directive string
        """
        # Extract domain if not provided
        if domain is None:
            domain, _ = self.extract_domain()
        
        # Select theme if not provided
        if theme is None:
            theme = self._select_theme()
        
        # Get color palette
        colors = self.get_color_palette(domain)
        
        # Build themeVariables
        theme_variables = {
            "primaryColor": colors["primary"],
            "primaryTextColor": colors["primaryText"],
            "primaryBorderColor": colors["primaryBorder"],
            "lineColor": colors["lineColor"],
            "secondaryColor": colors["secondary"],
            "tertiaryColor": colors["tertiary"],
        }
        
        # Format as JSON and convert to Mermaid syntax (single quotes)
        theme_vars_json = json.dumps(theme_variables)
        theme_vars_str = theme_vars_json.replace('"', "'")
        
        # Build init directive
        init_directive = f"%%{{init: {{'theme':'{theme}', 'themeVariables':{theme_vars_str}}}}}%%"
        
        logger.info(
            f"[StyleConfigGenerator] Init directive generated | domain={domain} | theme={theme} | "
            f"primaryColor={colors['primary']} | length={len(init_directive)} chars"
        )
        logger.debug(f"[StyleConfigGenerator] Init directive: {init_directive[:100]}...")
        
        return init_directive
    
    def generate_full_config(self, features: Optional[List] = None, stories: Optional[List] = None) -> Dict:
        """Generate full style configuration including complexity analysis.
        
        Args:
            features: Optional list of features
            stories: Optional list of stories
            
        Returns:
            Dictionary with style config, domain, complexity, and init directive
        """
        logger.debug("[StyleConfigGenerator] Generating full configuration")
        
        # Extract domain
        domain, all_domains = self.extract_domain()
        
        # Select theme
        theme = self._select_theme()
        
        # Get colors
        colors = self.get_color_palette(domain)
        
        # Analyze complexity
        complexity = self.analyze_complexity(features, stories)
        
        # Generate init directive
        init_directive = self.generate_init_directive(domain, theme)
        
        config = {
            "domain": domain,
            "all_domains": all_domains,
            "theme": theme,
            "colors": colors,
            "complexity": complexity,
            "init_directive": init_directive,
        }
        
        logger.info(
            f"[StyleConfigGenerator] Full config generated | domain={domain} | theme={theme} | "
            f"complexity_score={complexity['complexity_score']} | diagram_type={complexity['recommended_type']}"
        )
        
        return config


# Convenience function for backward compatibility
def generate_style_from_prompt(prompt: str, project_id: str = "") -> Dict:
    """Generate style configuration from prompt (backward compatibility).
    
    Args:
        prompt: Customer prompt
        project_id: Optional project ID
        
    Returns:
        Style configuration dictionary
    """
    generator = StyleConfigGenerator(prompt, project_id)
    config = generator.generate_full_config()
    
    # Convert to old format for compatibility
    return {
        "theme": config["theme"],
        "nodeShape": "rect",  # Default
        "primaryColor": config["colors"]["primary"],
        "secondaryColor": config["colors"]["secondary"],
        "accentColor": config["colors"]["tertiary"],
        "backgroundColor": "#ffffff",  # Default
        "arrowStyle": "solid",  # Default
        "fontSize": "16px",  # Default
        "fontFamily": "Arial, sans-serif",  # Default
        "domain": config["domain"],
        "init_directive": config["init_directive"],
        "complexity": config["complexity"],
    }

