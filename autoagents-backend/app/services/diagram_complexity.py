"""Diagram complexity analysis and shape variation logic for Agent 3."""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def analyze_complexity(
    features: List[Dict],
    stories: List[Dict],
    original_prompt: str = "",
) -> Dict[str, any]:
    """Analyze project complexity to determine appropriate diagram type.
    
    Args:
        features: List of feature dictionaries
        stories: List of story dictionaries
        original_prompt: Original user prompt
        
    Returns:
        Dictionary with complexity metrics and recommended diagram type
    """
    num_features = len(features) if features else 0
    num_stories = len(stories) if stories else 0
    
    # Analyze prompt for complexity indicators
    prompt_lower = (original_prompt or "").lower()
    
    # State-related keywords
    state_keywords = ["state", "status", "workflow", "process", "stage", "phase", "transition"]
    has_state_indicators = any(keyword in prompt_lower for keyword in state_keywords)
    
    # Data flow keywords
    data_flow_keywords = ["data flow", "pipeline", "stream", "process", "transform", "aggregate", "batch"]
    has_data_flow = any(keyword in prompt_lower for keyword in data_flow_keywords)
    
    # Workflow/complexity keywords
    workflow_keywords = ["workflow", "process", "sequence", "pipeline", "orchestration", "multi-step"]
    has_workflow = any(keyword in prompt_lower for keyword in workflow_keywords)
    
    # Calculate complexity score
    complexity_score = 0
    complexity_score += num_features * 2
    complexity_score += num_stories * 1
    if has_state_indicators:
        complexity_score += 10
    if has_data_flow:
        complexity_score += 8
    if has_workflow:
        complexity_score += 5
    
    # Determine diagram type based on complexity
    if has_state_indicators and complexity_score > 15:
        recommended_type = "stateDiagram-v2"
        reason = "State-heavy system detected"
    elif has_data_flow and complexity_score > 12:
        recommended_type = "graph TB"  # Top-bottom with subgraphs
        reason = "Data flow system detected"
    elif has_workflow or complexity_score > 10:
        recommended_type = "flowchart LR"  # Left-right for complex workflows
        reason = "Complex workflow detected"
    else:
        recommended_type = "flowchart TD"  # Simple top-down
        reason = "Simple system"
    
    result = {
        "complexity_score": complexity_score,
        "num_features": num_features,
        "num_stories": num_stories,
        "has_state_indicators": has_state_indicators,
        "has_data_flow": has_data_flow,
        "has_workflow": has_workflow,
        "recommended_type": recommended_type,
        "reason": reason,
    }
    
    logger.info(
        f"[diagram_complexity] Complexity analysis | score={complexity_score} | "
        f"features={num_features} | stories={num_stories} | type={recommended_type} | reason={reason}"
    )
    
    return result


def get_shape_guidance() -> Dict[str, str]:
    """Get shape variation guidance for different node types.
    
    Returns:
        Dictionary mapping node types to Mermaid shape syntax
    """
    return {
        "entry_point": "stadium",  # (EntryPoint) or ([EntryPoint])
        "process": "rect",  # [Process] or Process[Process]
        "decision": "diamond",  # {Decision} or Decision{Decision}
        "data_store": "cylinder",  # [(DataStore)] or DataStore[(DataStore)]
        "external": "parallelogram",  # [/External\] or External[/External\]
        "subgraph": "rect",  # subgraph name["Title"]
    }


def get_shape_syntax(node_type: str, node_name: str) -> str:
    """Get Mermaid syntax for a specific node type and name.
    
    Args:
        node_type: Type of node (entry_point, process, decision, data_store, external)
        node_name: Name of the node
        
    Returns:
        Mermaid syntax string for the node
    """
    shape_map = get_shape_guidance()
    
    if node_type == "entry_point":
        return f"({node_name})"  # Stadium/rounded
    elif node_type == "process":
        return f"[{node_name}]"  # Rectangle
    elif node_type == "decision":
        return f"{{{{{node_name}}}}}"  # Diamond (double braces)
    elif node_type == "data_store":
        return f"[({node_name})]"  # Cylinder
    elif node_type == "external":
        return f"[\\{node_name}/]"  # Parallelogram/trapezoid
    else:
        return f"[{node_name}]"  # Default rectangle


def build_shape_instructions() -> str:
    """Build instructions for shape usage in diagram generation.
    
    DEPRECATED: Use NodeShapeSelector.build_shape_instructions() instead.
    Kept for backward compatibility.
    
    Returns:
        String with shape usage instructions
    """
    return """
SHAPE VARIATION REQUIREMENTS:
- Entry points (user actions, system start): Use stadium/rounded shapes - (EntryPoint)
- Processes (business logic, transformations): Use rectangles - [Process]
- Decisions (conditionals, branches): Use diamonds - {Decision}
- Data stores (databases, caches, storage): Use cylinders - [(DataStore)]
- External systems (APIs, third-party services): Use parallelograms/trapezoids - [/External/]

Apply shapes consistently throughout the diagram based on node function.
"""


def get_diagram_type_guidance(diagram_type: str, complexity_info: Dict) -> str:
    """Get specific guidance for diagram type based on complexity.
    
    Args:
        diagram_type: Type of diagram (hld, lld, database)
        complexity_info: Complexity analysis results
        
    Returns:
        Guidance string for the diagram generation
    """
    recommended = complexity_info.get("recommended_type", "flowchart TD")
    
    if diagram_type.lower() == "hld":
        guidance = f"""
DIAGRAM TYPE: Use {recommended} for this High Level Design.

For {recommended}:
- Organize components logically based on flow direction
- Use subgraphs to group related components
- Show high-level interactions between major system parts
- Focus on business flow and user journey
"""
    elif diagram_type.lower() == "lld":
        guidance = f"""
DIAGRAM TYPE: Use {recommended} or classDiagram/sequenceDiagram for Low Level Design.

For detailed component design:
- Use classDiagram for class structures and relationships
- Use sequenceDiagram for interaction flows
- Use {recommended} for component-level flowcharts
- Show API endpoints, service layers, and data flow
"""
    else:  # database
        guidance = """
DIAGRAM TYPE: Use entityRelationshipDiagram for Database Design.

For database diagrams:
- Use entityRelationshipDiagram syntax
- Show tables, relationships, keys
- Include cardinality (one-to-one, one-to-many, many-to-many)
"""
    
    return guidance

