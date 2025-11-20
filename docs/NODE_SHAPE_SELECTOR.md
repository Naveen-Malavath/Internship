# NodeShapeSelector Documentation

## Overview

The `NodeShapeSelector` class provides intelligent node shape selection for Mermaid diagrams based on:
1. **Node Type**: controller, service, database, external API, user interface, decision
2. **Architectural Layer**: presentation, business logic, data, infrastructure
3. **Prompt Complexity**: simple systems use consistent shapes, complex systems allow variation

## Location

`autoagents-backend/app/services/node_shape_selector.py`

## Key Features

- **Automatic Node Type Detection**: Analyzes node names and context to detect type
- **Architectural Layer Mapping**: Maps nodes to presentation, business logic, data, or infrastructure layers
- **Complexity-Based Variation**: Adjusts shape consistency based on system complexity
- **Mermaid Syntax Generation**: Generates correct Mermaid syntax for each shape type
- **Comprehensive Debug Logging**: Extensive logging for troubleshooting

## Shape Mapping

### Node Type to Shape Mapping

| Node Type | Shape | Mermaid Syntax | Example |
|-----------|-------|----------------|---------|
| Controller/API | Stadium | `([text])` | `([UserController])` |
| Service | Rectangle | `[text]` | `[AuthService]` |
| Decision | Diamond | `{{text}}` | `{{ValidateUser}}` |
| Database | Cylinder | `[(text)]` | `[(UserDatabase)]` |
| External | Parallelogram | `[/text/]` | `[/PaymentGateway/]` |
| User Interface | Circle | `((text))` | `((LoginPage))` |

### Architectural Layer Mapping

- **Presentation Layer**: Controllers, APIs, User Interface
- **Business Logic Layer**: Services, Business Logic
- **Data Layer**: Databases, Data Stores
- **Infrastructure Layer**: External Systems, Third-party APIs

## Usage Examples

### Basic Usage

```python
from app.services.node_shape_selector import NodeShapeSelector

# Initialize with complexity score
selector = NodeShapeSelector(complexity_score=15, prompt="Build a banking app")

# Get Mermaid syntax for a node
controller_syntax = selector.get_mermaid_syntax("UserController", "controller")
# Returns: ([UserController])

service_syntax = selector.get_mermaid_syntax("AuthService", "service")
# Returns: [AuthService]

database_syntax = selector.get_mermaid_syntax("UserDatabase", "database")
# Returns: [(UserDatabase)]
```

### Automatic Node Type Detection

```python
selector = NodeShapeSelector(complexity_score=10)

# Detect node type from name
controller = selector.get_mermaid_syntax("UserController")
# Automatically detects "controller" type → ([UserController])

service = selector.get_mermaid_syntax("PaymentService")
# Automatically detects "service" type → [PaymentService]

decision = selector.get_mermaid_syntax("ValidateTransaction")
# Automatically detects "decision" type → {{ValidateTransaction}}
```

### With Context

```python
selector = NodeShapeSelector(complexity_score=12)

# Provide context for better detection
node = selector.get_mermaid_syntax(
    "API", 
    context="REST endpoint for user authentication"
)
# Detects as controller → ([API])
```

### Complexity-Based Instructions

```python
# Simple system (score < 10)
simple_selector = NodeShapeSelector(complexity_score=5)
instructions = simple_selector.build_shape_instructions()
# Instructions emphasize strict consistency

# Complex system (score >= 15)
complex_selector = NodeShapeSelector(complexity_score=20)
instructions = complex_selector.build_shape_instructions()
# Instructions allow slight variation for visual distinction
```

## Methods

### `__init__(complexity_score: int = 0, prompt: str = "")`

Initialize NodeShapeSelector.

**Parameters**:
- `complexity_score`: Complexity score from analysis
- `prompt`: Original prompt for consistency

### `detect_node_type(node_name: str, context: Optional[str] = None) -> str`

Detect node type from node name and context.

**Detection Patterns**:
- **Controller**: "controller", "api", "endpoint", "route", "handler"
- **Service**: "service", "business", "logic", "manager", "handler"
- **Decision**: "decision", "if", "condition", "check", "validate"
- **Database**: "database", "db", "store", "cache", "repository", "data"
- **External**: "external", "third-party", "integration", "api call"
- **User Interface**: "user", "ui", "interface", "frontend", "page", "component"

**Returns**: Detected node type string

### `detect_architectural_layer(node_name: str, context: Optional[str] = None) -> str`

Detect architectural layer from node name and context.

**Returns**: Layer name ("presentation", "business_logic", "data", "infrastructure")

### `get_mermaid_syntax(node_name: str, node_type: Optional[str] = None, layer: Optional[str] = None, context: Optional[str] = None) -> str`

Get Mermaid syntax for a node.

**Parameters**:
- `node_name`: Name of the node
- `node_type`: Optional explicit node type
- `layer`: Optional architectural layer
- `context`: Optional context for detection

**Returns**: Mermaid syntax string

### `build_shape_instructions(complexity_info: Optional[Dict] = None) -> str`

Build comprehensive shape usage instructions for diagram generation.

**Returns**: Detailed instructions string with examples

### `get_shape_mapping_summary() -> Dict[str, str]`

Get summary of shape mappings.

**Returns**: Dictionary mapping node types to shape information

### `get_example_nodes() -> Dict[str, str]`

Get example node syntax for each node type.

**Returns**: Dictionary with example Mermaid syntax for each type

### `validate_node_syntax(node_syntax: str) -> bool`

Validate Mermaid node syntax.

**Returns**: True if syntax is valid

## Integration with Agent 3

The `NodeShapeSelector` is integrated into Agent 3's diagram generation:

```python
# In agent3.py
shape_selector = NodeShapeSelector(
    complexity_score=complexity_info["complexity_score"],
    prompt=original_prompt
)

# Get shape instructions for prompt
shape_instructions = shape_selector.build_shape_instructions(complexity_info)

# Include in Claude prompt
user_prompt = f"""
{shape_instructions}
...
"""
```

## Complexity-Based Behavior

### Simple Systems (score < 10)
- **Strict Consistency**: All controllers use stadium, all services use rectangles
- **No Variation**: Shapes are consistent throughout the diagram
- **Clear Mapping**: One-to-one mapping between node type and shape

### Complex Systems (score >= 15)
- **Slight Variation**: May vary shapes slightly for visual distinction
- **Subgraph Grouping**: Uses subgraphs to group related components
- **Layer-Based Organization**: Groups nodes by architectural layer

## Debug Logging

The class includes comprehensive debug logging:

```
[NodeShapeSelector] Initialized | complexity_score=15 | is_simple=False | is_complex=True
[NodeShapeSelector] Node type detected | node=UserController | type=controller
[NodeShapeSelector] Layer detected | node=UserController | layer=presentation
[NodeShapeSelector] Shape for node type | type=controller | shape=stadium
[NodeShapeSelector] Mermaid syntax generated | node=UserController | type=controller | shape=stadium | syntax=([UserController])...
[NodeShapeSelector] Shape instructions built | length=1234 chars
[NodeShapeSelector] Shape mapping summary generated | 6 mappings
[NodeShapeSelector] Example nodes generated | 6 examples
```

## Example Output

### Shape Instructions Example

```
NODE SHAPE REQUIREMENTS (Complexity Score: 15):

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

EXAMPLES:
- UserController → ([UserController])
- AuthService → [AuthService]
- ValidateUser → {{ValidateUser}}
- UserDatabase → [(UserDatabase)]
- PaymentGateway → [/PaymentGateway/]
- LoginPage → ((LoginPage))
```

## Testing

### Test Node Type Detection

```python
selector = NodeShapeSelector(complexity_score=10)

# Test controller detection
assert selector.detect_node_type("UserController") == "controller"
assert selector.detect_node_type("API", "REST endpoint") == "controller"

# Test service detection
assert selector.detect_node_type("AuthService") == "service"
assert selector.detect_node_type("BusinessLogic") == "service"

# Test database detection
assert selector.detect_node_type("UserDatabase") == "database"
assert selector.detect_node_type("Cache", "data store") == "database"
```

### Test Mermaid Syntax Generation

```python
selector = NodeShapeSelector(complexity_score=10)

# Test stadium (controller)
syntax = selector.get_mermaid_syntax("UserController", "controller")
assert syntax == "([UserController])"

# Test rectangle (service)
syntax = selector.get_mermaid_syntax("AuthService", "service")
assert syntax == "[AuthService]"

# Test diamond (decision)
syntax = selector.get_mermaid_syntax("ValidateUser", "decision")
assert syntax == "{{ValidateUser}}"

# Test cylinder (database)
syntax = selector.get_mermaid_syntax("UserDatabase", "database")
assert syntax == "[(UserDatabase)]"

# Test parallelogram (external)
syntax = selector.get_mermaid_syntax("PaymentGateway", "external")
assert syntax == "[\\PaymentGateway/]"

# Test circle (UI)
syntax = selector.get_mermaid_syntax("LoginPage", "user_interface")
assert syntax == "((LoginPage))"
```

### Test Complexity-Based Instructions

```python
# Simple system
simple_selector = NodeShapeSelector(complexity_score=5)
simple_instructions = simple_selector.build_shape_instructions()
assert "SIMPLE SYSTEM" in simple_instructions
assert "consistent shapes" in simple_instructions.lower()

# Complex system
complex_selector = NodeShapeSelector(complexity_score=20)
complex_instructions = complex_selector.build_shape_instructions()
assert "COMPLEX SYSTEM" in complex_instructions
assert "vary shapes" in complex_instructions.lower()
```

## Error Handling

The class handles edge cases gracefully:

- **Empty node name**: Returns "Node" as default
- **Unknown node type**: Defaults to "service" (rectangle)
- **Invalid syntax**: Validation method catches issues
- **Long node names**: Automatically truncated to 50 characters
- **Special characters**: Properly escaped for Mermaid syntax

## Future Enhancements

Potential improvements:
1. Custom shape mappings per domain
2. User-defined node type patterns
3. Shape color coordination with style config
4. Multi-language node name support
5. Shape animation styles
6. Export/import shape configurations

