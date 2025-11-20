"""Node shape selector for Mermaid diagrams based on node type, architectural layer, and complexity."""

import hashlib
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class NodeShapeSelector:
    """Selects and generates Mermaid node shapes based on node type, layer, and complexity."""
    
    # Node type to shape mapping
    NODE_TYPE_SHAPES = {
        "controller": "stadium",      # Controllers/APIs → ([text])
        "api": "stadium",             # API endpoints → ([text])
        "service": "rectangle",       # Services → [text]
        "business_logic": "rectangle", # Business logic → [text]
        "decision": "diamond",         # Decisions → {text}
        "database": "cylinder",        # Databases → [("text")]
        "data_store": "cylinder",     # Data stores → [("text")]
        "external": "parallelogram",  # External systems → [/"text"/]
        "external_api": "parallelogram", # External APIs → [/"text"/]
        "user_interface": "circle",   # User actions/UI → ((text))
        "user_action": "circle",      # User actions → ((text))
        "ui": "circle",               # UI components → ((text))
    }
    
    # Architectural layer mapping
    ARCHITECTURAL_LAYERS = {
        "presentation": ["controller", "api", "user_interface", "ui", "user_action"],
        "business_logic": ["service", "business_logic"],
        "data": ["database", "data_store"],
        "infrastructure": ["external", "external_api"],
    }
    
    # Complexity thresholds
    SIMPLE_COMPLEXITY_THRESHOLD = 10
    COMPLEX_COMPLEXITY_THRESHOLD = 15
    
    def __init__(self, complexity_score: int = 0, prompt: str = ""):
        """Initialize NodeShapeSelector.
        
        Args:
            complexity_score: Complexity score from analysis
            prompt: Original prompt for consistency
        """
        self.complexity_score = complexity_score
        self.prompt = prompt or ""
        self.is_simple = complexity_score < self.SIMPLE_COMPLEXITY_THRESHOLD
        self.is_complex = complexity_score >= self.COMPLEX_COMPLEXITY_THRESHOLD
        
        logger.debug(
            f"[NodeShapeSelector] Initialized | complexity_score={complexity_score} | "
            f"is_simple={self.is_simple} | is_complex={self.is_complex}"
        )
    
    def detect_node_type(self, node_name: str, context: Optional[str] = None) -> str:
        """Detect node type from node name and context.
        
        Args:
            node_name: Name of the node
            context: Optional context or description
            
        Returns:
            Detected node type
        """
        name_lower = (node_name or "").lower()
        context_lower = (context or "").lower()
        combined = f"{name_lower} {context_lower}"
        
        # Detection patterns
        if any(keyword in combined for keyword in ["controller", "api", "endpoint", "route", "handler"]):
            node_type = "controller"
        elif any(keyword in combined for keyword in ["service", "business", "logic", "manager", "handler"]):
            node_type = "service"
        elif any(keyword in combined for keyword in ["decision", "if", "condition", "check", "validate"]):
            node_type = "decision"
        elif any(keyword in combined for keyword in ["database", "db", "store", "cache", "repository", "data"]):
            node_type = "database"
        elif any(keyword in combined for keyword in ["external", "third-party", "integration", "api call"]):
            node_type = "external"
        elif any(keyword in combined for keyword in ["user", "ui", "interface", "frontend", "page", "component"]):
            node_type = "user_interface"
        else:
            node_type = "service"  # Default to service/rectangle
        
        logger.debug(f"[NodeShapeSelector] Node type detected | node={node_name} | type={node_type}")
        return node_type
    
    def detect_architectural_layer(self, node_name: str, context: Optional[str] = None) -> str:
        """Detect architectural layer from node name and context.
        
        Args:
            node_name: Name of the node
            context: Optional context or description
            
        Returns:
            Detected architectural layer
        """
        node_type = self.detect_node_type(node_name, context)
        
        # Map node type to layer
        for layer, node_types in self.ARCHITECTURAL_LAYERS.items():
            if node_type in node_types:
                logger.debug(f"[NodeShapeSelector] Layer detected | node={node_name} | layer={layer}")
                return layer
        
        # Default to business logic
        logger.debug(f"[NodeShapeSelector] Default layer | node={node_name} | layer=business_logic")
        return "business_logic"
    
    def get_shape_for_node_type(self, node_type: str) -> str:
        """Get shape name for a node type.
        
        Args:
            node_type: Type of node
            
        Returns:
            Shape name (stadium, rectangle, diamond, cylinder, parallelogram, circle)
        """
        shape = self.NODE_TYPE_SHAPES.get(node_type, "rectangle")  # Default to rectangle
        logger.debug(f"[NodeShapeSelector] Shape for node type | type={node_type} | shape={shape}")
        return shape
    
    def get_mermaid_syntax(self, node_name: str, node_type: Optional[str] = None, 
                          layer: Optional[str] = None, context: Optional[str] = None) -> str:
        """Get Mermaid syntax for a node.
        
        Args:
            node_name: Name of the node
            node_type: Optional explicit node type
            layer: Optional architectural layer
            context: Optional context for detection
            
        Returns:
            Mermaid syntax string for the node
        """
        # Detect node type if not provided
        if node_type is None:
            node_type = self.detect_node_type(node_name, context)
        
        # Get shape
        shape = self.get_shape_for_node_type(node_type)
        
        # Generate Mermaid syntax based on shape
        syntax = self._generate_syntax(node_name, shape, node_type)
        
        logger.debug(
            f"[NodeShapeSelector] Mermaid syntax generated | node={node_name} | "
            f"type={node_type} | shape={shape} | syntax={syntax[:50]}..."
        )
        
        return syntax
    
    def _generate_syntax(self, node_name: str, shape: str, node_type: str) -> str:
        """Generate Mermaid syntax for a specific shape.
        
        Args:
            node_name: Name of the node
            shape: Shape name
            node_type: Node type for special cases
            
        Returns:
            Mermaid syntax string
        """
        # Escape node name for Mermaid
        escaped_name = self._escape_node_name(node_name)
        
        if shape == "stadium":
            # Controllers/APIs → ([text])
            return f"([{escaped_name}])"
        elif shape == "rectangle":
            # Services → [text]
            return f"[{escaped_name}]"
        elif shape == "diamond":
            # Decisions → {{text}}
            return f"{{{{{escaped_name}}}}}"
        elif shape == "cylinder":
            # Databases → [("text")]
            return f"[({escaped_name})]"
        elif shape == "parallelogram":
            # External → [/"text"/]
            return f"[\\{escaped_name}/]"
        elif shape == "circle":
            # User actions → ((text))
            return f"(({escaped_name}))"
        else:
            # Default to rectangle
            return f"[{escaped_name}]"
    
    def _escape_node_name(self, node_name: str) -> str:
        """Escape node name for Mermaid syntax.
        
        Args:
            node_name: Original node name
            
        Returns:
            Escaped node name
        """
        if not node_name:
            return "Node"
        
        # Remove or escape special Mermaid characters
        escaped = node_name.replace('"', "'")
        escaped = escaped.replace('\n', ' ')
        escaped = escaped.replace('\r', ' ')
        escaped = ' '.join(escaped.split())  # Normalize whitespace
        
        # Truncate if too long
        if len(escaped) > 50:
            escaped = escaped[:47] + "..."
        
        return escaped
    
    def build_shape_instructions(self, complexity_info: Optional[Dict] = None) -> str:
        """Build comprehensive shape usage instructions for diagram generation.
        
        Args:
            complexity_info: Optional complexity information
            
        Returns:
            String with shape usage instructions
        """
        complexity_score = complexity_info.get("complexity_score", self.complexity_score) if complexity_info else self.complexity_score
        is_simple = complexity_score < self.SIMPLE_COMPLEXITY_THRESHOLD
        
        instructions = f"""
NODE SHAPE REQUIREMENTS (Complexity Score: {complexity_score}):

Apply shapes consistently based on node type and architectural layer:

ARCHITECTURAL LAYERS:
- Presentation Layer (Controllers, APIs, UI):
  * Controllers/API Endpoints → ([ControllerName])  (stadium shape)
  * User Interface/User Actions → ((UIName))  (circle shape)

- Business Logic Layer (Services):
  * Services/Business Logic → [ServiceName]  (rectangle shape)
  * Process/Transform → [ProcessName]  (rectangle shape)

- Data Layer:
  * Databases/Data Stores → [(DatabaseName)]  (cylinder shape)
  * Caches/Repositories → [(StoreName)]  (cylinder shape)

- Infrastructure Layer:
  * External Systems/APIs → [/ExternalName/]  (parallelogram shape)
  * Third-party Integrations → [/IntegrationName/]  (parallelogram shape)

- Decision Points:
  * Conditionals/Branches → {{DecisionName}}  (diamond shape)
  * Validation/Checks → {{CheckName}}  (diamond shape)

SHAPE CONSISTENCY:
"""
        
        if is_simple:
            instructions += """
- SIMPLE SYSTEM: Use consistent shapes throughout. Stick to the mapping above strictly.
- All controllers should use stadium shape, all services should use rectangles, etc.
"""
        else:
            instructions += """
- COMPLEX SYSTEM: You may vary shapes slightly for visual distinction, but maintain consistency within each node type category.
- Use subgraphs to group related components by architectural layer.
"""
        
        instructions += """
EXAMPLES:
- UserController → ([UserController])
- AuthService → [AuthService]
- ValidateUser → {{ValidateUser}}
- UserDatabase → [(UserDatabase)]
- PaymentGateway → [/PaymentGateway/]
- LoginPage → ((LoginPage))

Apply these shapes consistently throughout the diagram.
"""
        
        logger.debug(f"[NodeShapeSelector] Shape instructions built | length={len(instructions)} chars")
        return instructions
    
    def get_shape_mapping_summary(self) -> Dict[str, str]:
        """Get summary of shape mappings.
        
        Returns:
            Dictionary mapping node types to Mermaid syntax examples
        """
        summary = {}
        for node_type, shape in self.NODE_TYPE_SHAPES.items():
            example_name = node_type.replace("_", " ").title()
            syntax = self._generate_syntax(example_name, shape, node_type)
            summary[node_type] = {
                "shape": shape,
                "example": syntax,
            }
        
        logger.debug(f"[NodeShapeSelector] Shape mapping summary generated | {len(summary)} mappings")
        return summary
    
    def validate_node_syntax(self, node_syntax: str) -> bool:
        """Validate Mermaid node syntax.
        
        Args:
            node_syntax: Mermaid node syntax string
            
        Returns:
            True if syntax is valid, False otherwise
        """
        valid_patterns = [
            r"^\(\[.*\]\)$",      # Stadium: ([text])
            r"^\[.*\]$",          # Rectangle: [text]
            r"^\{\{.*\}\}$",      # Diamond: {{text}}
            r"^\[\(.*\)\]$",      # Cylinder: [(text)]
            r"^\[\\[^/]*/\]$",    # Parallelogram: [\text/]
            r"^\(\(.*\)\)$",      # Circle: ((text))
        ]
        
        import re
        is_valid = any(re.match(pattern, node_syntax) for pattern in valid_patterns)
        
        logger.debug(f"[NodeShapeSelector] Syntax validation | syntax={node_syntax[:30]}... | valid={is_valid}")
        return is_valid
    
    def get_example_nodes(self) -> Dict[str, str]:
        """Get example node syntax for each node type.
        
        Returns:
            Dictionary mapping node types to example Mermaid syntax
        """
        examples = {
            "controller": self.get_mermaid_syntax("UserController", "controller"),
            "service": self.get_mermaid_syntax("AuthService", "service"),
            "decision": self.get_mermaid_syntax("ValidateUser", "decision"),
            "database": self.get_mermaid_syntax("UserDatabase", "database"),
            "external": self.get_mermaid_syntax("PaymentGateway", "external"),
            "user_interface": self.get_mermaid_syntax("LoginPage", "user_interface"),
        }
        
        logger.debug(f"[NodeShapeSelector] Example nodes generated | {len(examples)} examples")
        return examples

