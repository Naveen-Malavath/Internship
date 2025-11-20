# StyleConfigGenerator Class Documentation

## Overview

The `StyleConfigGenerator` class is a comprehensive solution for generating Mermaid diagram style configurations based on customer prompts. It extracts domain indicators, maps them to color palettes, and generates Mermaid %%init%% configuration directives.

## Location

`autoagents-backend/app/services/style_config_generator.py`

## Key Features

1. **Domain Extraction**: Analyzes customer prompts to identify domain keywords
2. **Color Palette Mapping**: Maps domains to specific color schemes
3. **Complexity Analysis**: Determines diagram type based on architecture complexity
4. **Init Directive Generation**: Creates Mermaid %%init%% configuration strings
5. **Comprehensive Debug Logging**: Extensive logging for troubleshooting

## Class Structure

### Initialization

```python
generator = StyleConfigGenerator(prompt: str, project_id: str = "")
```

**Parameters**:
- `prompt`: Customer prompt text
- `project_id`: Optional project ID for consistency

### Domain Keyword Mappings

The class includes enhanced domain keyword mappings:

- **E-commerce**: shop, shopping, store, e-commerce, retail, marketplace, cart, checkout, product, catalog, purchase, buy, sell, merchant, vendor
- **Healthcare**: hospital, clinic, healthcare, health, medical, patient, doctor, physician, nurse, pharmacy, diagnosis, treatment, appointment, prescription
- **Finance**: bank, banking, finance, financial, payment, transaction, account, investment, wallet, credit, loan, mortgage, trading, stock, portfolio
- **Education**: school, university, college, education, learning, student, teacher, professor, course, curriculum, academic, training, lesson, assignment, grade
- **Tech/AI**: ai, artificial intelligence, machine learning, ml, iot, internet of things, technology, tech, software, application, system, platform, api, development, algorithm, neural, deep learning, data science, analytics, automation
- **Logistics**: logistics, shipping, delivery, supply chain, warehouse, inventory, transport, freight, distribution, fulfillment
- **Social**: social, community, network, chat, messaging, forum, profile, social media, connect, share, follow

### Color Palettes

Domain-specific color palettes as requested:

#### E-commerce: Blues and Oranges
```python
{
    "primary": "#2563EB",      # Blue
    "primaryText": "#FFFFFF",
    "primaryBorder": "#1E40AF", # Darker blue
    "lineColor": "#3B82F6",     # Light blue
    "secondary": "#F97316",     # Orange
    "tertiary": "#FB923C",       # Light orange
}
```

#### Healthcare: Greens and Whites
```python
{
    "primary": "#10B981",       # Green
    "primaryText": "#FFFFFF",
    "primaryBorder": "#059669", # Darker green
    "lineColor": "#34D399",     # Light green
    "secondary": "#F9FAFB",     # White
    "tertiary": "#E5E7EB",      # Light gray
}
```

#### Finance: Navy and Gold
```python
{
    "primary": "#1E3A8A",       # Navy
    "primaryText": "#FFFFFF",
    "primaryBorder": "#1E40AF", # Darker navy
    "lineColor": "#3B82F6",    # Blue
    "secondary": "#F59E0B",     # Gold
    "tertiary": "#FBBF24",      # Light gold
}
```

#### Education: Purples and Yellows
```python
{
    "primary": "#7C3AED",       # Purple
    "primaryText": "#FFFFFF",
    "primaryBorder": "#6D28D9", # Darker purple
    "lineColor": "#A78BFA",     # Light purple
    "secondary": "#FCD34D",     # Yellow
    "tertiary": "#FDE047",      # Light yellow
}
```

#### Tech/AI: Cyans and Dark Grays
```python
{
    "primary": "#06B6D4",       # Cyan
    "primaryText": "#FFFFFF",
    "primaryBorder": "#0891B2", # Darker cyan
    "lineColor": "#22D3EE",     # Light cyan
    "secondary": "#374151",     # Dark gray
    "tertiary": "#4B5563",      # Medium gray
}
```

## Methods

### `extract_domain() -> Tuple[str, List[str]]`

Extracts domain from prompt using keyword matching with scoring.

**Returns**:
- Primary domain (highest score)
- List of all detected domains

**Example**:
```python
generator = StyleConfigGenerator("Build an online shopping store")
domain, all_domains = generator.extract_domain()
# domain = "e-commerce"
# all_domains = ["e-commerce"]
```

### `analyze_complexity(features=None, stories=None) -> Dict`

Analyzes architecture complexity to determine appropriate diagram type.

**Parameters**:
- `features`: Optional list of features
- `stories`: Optional list of stories

**Returns**:
```python
{
    "complexity_score": 18,
    "num_features": 5,
    "num_stories": 12,
    "has_state_indicators": True,
    "has_data_flow": False,
    "has_workflow": True,
    "recommended_type": "stateDiagram-v2",
    "reason": "State-heavy system detected"
}
```

**Complexity Scoring**:
- Features: 2 points each
- Stories: 1 point each
- State indicators: +10 points
- Data flow indicators: +8 points
- Workflow indicators: +5 points

**Diagram Type Selection**:
- **Simple** (score < 10): `flowchart TD`
- **Complex workflows** (score 10-15): `flowchart LR`
- **State-heavy** (score > 15 + state): `stateDiagram-v2`
- **Data flows** (score > 12 + data flow): `graph TB`

### `generate_init_directive(domain=None, theme=None) -> str`

Generates Mermaid %%init%% configuration directive.

**Parameters**:
- `domain`: Optional domain override
- `theme`: Optional theme override

**Returns**:
```mermaid
%%{init: {'theme':'base', 'themeVariables':{'primaryColor':'#2563EB', 'primaryTextColor':'#FFFFFF', 'primaryBorderColor':'#1E40AF', 'lineColor':'#3B82F6', 'secondaryColor':'#F97316', 'tertiaryColor':'#FB923C'}}}%%
```

**Example**:
```python
generator = StyleConfigGenerator("Build a banking app")
directive = generator.generate_init_directive()
# Returns: %%{init: {'theme':'base', 'themeVariables':{...}}}%%
```

### `generate_full_config(features=None, stories=None) -> Dict`

Generates complete style configuration including complexity analysis.

**Returns**:
```python
{
    "domain": "finance",
    "all_domains": ["finance"],
    "theme": "base",
    "colors": {
        "primary": "#1E3A8A",
        "primaryText": "#FFFFFF",
        "primaryBorder": "#1E40AF",
        "lineColor": "#3B82F6",
        "secondary": "#F59E0B",
        "tertiary": "#FBBF24"
    },
    "complexity": {
        "complexity_score": 15,
        "recommended_type": "flowchart LR",
        ...
    },
    "init_directive": "%%{init: {...}}%%"
}
```

## Usage Examples

### Basic Usage

```python
from app.services.style_config_generator import StyleConfigGenerator

# Initialize with customer prompt
generator = StyleConfigGenerator(
    prompt="Build a healthcare patient management system",
    project_id="proj_123"
)

# Generate full configuration
config = generator.generate_full_config()

# Get init directive
init_directive = config["init_directive"]

# Get complexity analysis
complexity = config["complexity"]
recommended_type = complexity["recommended_type"]
```

### With Features and Stories

```python
features = [{"title": "User Login"}, {"title": "Patient Records"}]
stories = [{"user_story": "As a doctor..."}, ...]

generator = StyleConfigGenerator("Build a hospital management system")
config = generator.generate_full_config(features, stories)

# Access complexity score
score = config["complexity"]["complexity_score"]
diagram_type = config["complexity"]["recommended_type"]
```

### Domain-Specific Styling

```python
# E-commerce example
generator = StyleConfigGenerator("Create an online shopping platform")
config = generator.generate_full_config()

# Colors will be blues and oranges
assert config["colors"]["primary"] == "#2563EB"  # Blue
assert config["colors"]["secondary"] == "#F97316"  # Orange

# Healthcare example
generator = StyleConfigGenerator("Build a hospital patient system")
config = generator.generate_full_config()

# Colors will be greens and whites
assert config["colors"]["primary"] == "#10B981"  # Green
assert config["colors"]["secondary"] == "#F9FAFB"  # White
```

## Integration with Agent 3

The `StyleConfigGenerator` is integrated into Agent 3's diagram generation process:

```python
# In agent3.py
style_generator = StyleConfigGenerator(original_prompt, project_title)
full_config = style_generator.generate_full_config(features, stories)

# Extract init directive
init_directive = full_config["init_directive"]

# Apply to Mermaid diagram
styled_mermaid = f"{init_directive}\n{mermaid}"
```

## Debug Logging

The class includes comprehensive debug logging:

```
[StyleConfigGenerator] Initialized | prompt_length=45 | project_id=proj_123
[StyleConfigGenerator] Domain extracted | primary=e-commerce | score=3 | keywords=['shop', 'store', 'cart']
[StyleConfigGenerator] Theme selected | theme=base
[StyleConfigGenerator] Color palette retrieved | domain=e-commerce | primary=#2563EB
[StyleConfigGenerator] Complexity analyzed | score=12 | type=flowchart LR | reason=Complex workflow detected
[StyleConfigGenerator] Init directive generated | domain=e-commerce | theme=base | primaryColor=#2563EB | length=234 chars
[StyleConfigGenerator] Full config generated | domain=e-commerce | theme=base | complexity_score=12 | diagram_type=flowchart LR
```

## Backward Compatibility

A convenience function is provided for backward compatibility:

```python
from app.services.style_config_generator import generate_style_from_prompt

# Old function-style API still works
config = generate_style_from_prompt("Build a shop", "proj_123")
```

## Testing

### Test Domain Extraction

```python
# Test e-commerce
generator = StyleConfigGenerator("Build an online shop")
domain, _ = generator.extract_domain()
assert domain == "e-commerce"

# Test healthcare
generator = StyleConfigGenerator("Create a hospital management system")
domain, _ = generator.extract_domain()
assert domain == "healthcare"

# Test tech/AI
generator = StyleConfigGenerator("Build an AI-powered IoT platform")
domain, _ = generator.extract_domain()
assert domain == "tech-ai"
```

### Test Color Palettes

```python
generator = StyleConfigGenerator("Build a bank")
colors = generator.get_color_palette("finance")
assert colors["primary"] == "#1E3A8A"  # Navy
assert colors["secondary"] == "#F59E0B"  # Gold
```

### Test Complexity Analysis

```python
features = [{"title": "Feature 1"}] * 5
stories = [{"user_story": "Story 1"}] * 10

generator = StyleConfigGenerator("Build a state management system")
complexity = generator.analyze_complexity(features, stories)
assert complexity["complexity_score"] > 15
assert complexity["recommended_type"] == "stateDiagram-v2"
```

## Error Handling

The class handles edge cases gracefully:

- **Empty prompt**: Returns "default" domain with default colors
- **No domain match**: Falls back to "default" domain
- **Missing features/stories**: Complexity analysis works with None values
- **Invalid colors**: Uses default color palette

## Future Enhancements

Potential improvements:
1. Custom domain keyword mappings
2. User-defined color palettes
3. Theme customization
4. Gradient color support
5. Animation styles
6. Export/import configurations

