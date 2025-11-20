# Dynamic Mermaid Diagram Styling System

## Overview

This document explains the dynamic Mermaid diagram styling system that generates unique visual styles based on the customer's domain/prompt. The system analyzes the prompt, extracts domain keywords, and creates consistent style configurations using deterministic hashing.

## Architecture Flow

### 1. Backend Style Generation (`mermaid_style_generator.py`)

**Location**: `autoagents-backend/app/services/mermaid_style_generator.py`

**Key Functions**:

- `extract_domain_keywords(prompt: str) -> List[str]`
  - Analyzes the prompt text to detect domain keywords
  - Supported domains: e-commerce, healthcare, finance, education, technology, social, entertainment, logistics
  - Returns list of detected domains

- `deterministic_hash(text: str, seed: int = 0) -> int`
  - Generates a consistent hash from text using SHA-256
  - Ensures same prompt always produces same hash

- `generate_style_from_prompt(prompt: str, project_id: str = "") -> MermaidStyleConfig`
  - Main function that generates complete style configuration
  - Uses hash to deterministically select:
    - Theme (default, forest, dark, neutral, base)
    - Node shapes (round, rect, stadium, circle, diamond, hexagon, parallelogram)
    - Arrow styles (solid, dotted, thick)
    - Font families and sizes
  - Selects domain-specific color schemes based on detected domain
  - Returns `MermaidStyleConfig` dictionary

- `apply_style_to_mermaid(mermaid_source: str, style_config: MermaidStyleConfig) -> str`
  - Injects Mermaid styling directives into diagram source code
  - Adds classDef definitions for node styling
  - Prepends style directives to diagram

**Style Configuration Structure**:
```python
{
    "theme": "forest",
    "nodeShape": "round",
    "primaryColor": "#5DADE2",
    "secondaryColor": "#58D68D",
    "accentColor": "#F7DC6F",
    "backgroundColor": "#EBF5FB",
    "arrowStyle": "solid",
    "fontSize": "16px",
    "fontFamily": "Arial, sans-serif",
    "domain": "healthcare"
}
```

### 2. Backend Integration

**Agent3 Service** (`agent3.py`):
- Updated `generate_mermaid()` to generate and apply styles
- Styles are applied to Mermaid source code before returning

**Diagram Router** (`routers/diagrams.py`):
- Generates style config when creating diagrams
- Stores `style_config` in database alongside `mermaid_source`
- Style config is included in API responses

**Diagram Schema** (`schemas/diagram.py`):
- Added optional `style_config: Optional[Dict]` field to `DiagramModel`

**Design Generation** (`agent3.py::generate_designs_for_project`):
- Generates consistent style config for all three diagrams (HLD, LLD, DBD)
- Stores style config in designs collection

### 3. Frontend Style Service (`mermaid-style.service.ts`)

**Location**: `autoagents-frontend/src/app/services/mermaid-style.service.ts`

**Key Functions**:

- `generateMermaidConfig(styleConfig, options) -> MermaidInitConfig`
  - Converts backend style configuration to Mermaid initialization options
  - Handles diagram-specific options (LLD spacing, padding, etc.)
  - Generates color variations (darken/lighten) for borders and lines
  - Returns complete Mermaid initialization configuration

**MermaidInitConfig Structure**:
```typescript
{
  startOnLoad: false,
  theme: "forest",
  themeVariables: {
    fontSize: "16px",
    fontFamily: "Arial, sans-serif",
    primaryColor: "#5DADE2",
    primaryTextColor: "#fff",
    primaryBorderColor: "#4A9BCE",
    lineColor: "#64748b",
    secondaryColor: "#58D68D",
    tertiaryColor: "#F7DC6F",
    background: "#EBF5FB"
  },
  flowchart: {
    useMaxWidth: false,
    htmlLabels: true,
    curve: "basis",
    padding: 20,
    nodeSpacing: 50,
    rankSpacing: 60
  }
}
```

### 4. Frontend Component Integration

**WorkspaceViewComponent** (`workspace-view.component.ts`):
- Added `@Input() mermaidStyleConfig: MermaidStyleConfig | null = null`
- Updated `renderMermaid()` to use `MermaidStyleService.generateMermaidConfig()`
- Applies dynamic styles when initializing Mermaid
- Falls back to default styles if no style config provided

## Data Flow

```
1. User creates project with prompt
   ↓
2. Backend generates diagram via Agent3
   ↓
3. mermaid_style_generator.generate_style_from_prompt()
   - Extracts domain keywords
   - Generates deterministic hash
   - Selects style options
   - Returns style_config
   ↓
4. Style config stored in database with diagram
   ↓
5. Frontend fetches diagram + style_config
   ↓
6. MermaidStyleService.generateMermaidConfig()
   - Converts style_config to Mermaid init options
   ↓
7. mermaid.initialize() with dynamic config
   ↓
8. Diagram rendered with domain-specific styling
```

## Domain-Specific Color Schemes

The system includes predefined color palettes for different domains:

- **E-commerce**: Coral red (#FF6B6B), Teal (#4ECDC4), Yellow (#FFE66D)
- **Healthcare**: Medical blue (#5DADE2), Health green (#58D68D), Light yellow (#F7DC6F)
- **Finance**: Banking green (#1E8449), Trust blue (#2874A6), Gold (#F39C12)
- **Education**: Learning blue (#3498DB), Creative purple (#9B59B6), Alert red (#E74C3C)
- **Technology**: Tech dark blue (#2C3E50), Tech blue (#3498DB), Tech red (#E74C3C)
- **Social**: Social blue (#4267B2), Twitter blue (#1DA1F2), Instagram pink (#E1306C)
- **Entertainment**: Entertainment red (#E74C3C), Creative purple (#9B59B6), Orange (#F39C12)
- **Logistics**: Logistics teal (#16A085), Orange (#F39C12), Dark orange (#E67E22)
- **Default**: Default blue (#3b82f6), Default green (#10b981), Default orange (#f59e0b)

## Deterministic Hashing

The system uses SHA-256 hashing to ensure:
- Same prompt + project_id = same style configuration
- Consistent styling across related diagrams
- No randomness in style selection

Hash is used to select:
- Theme index = hash % 5 (themes)
- Node shape index = (hash + 1) % 7 (shapes)
- Arrow style index = (hash + 2) % 3 (styles)
- Font family index = (hash + 3) % 5 (fonts)
- Font size index = (hash + 4) % 4 (sizes)

## Storage

Style configurations are stored:
- In `diagrams` collection: `style_config` field per diagram
- In `designs` collection: `style_config` field shared across HLD/LLD/DBD

## API Response Format

When fetching a diagram, the API returns:
```json
{
  "id": "...",
  "project_id": "...",
  "diagram_type": "hld",
  "mermaid_source": "graph TD\n...",
  "style_config": {
    "theme": "forest",
    "nodeShape": "round",
    "primaryColor": "#5DADE2",
    "secondaryColor": "#58D68D",
    "accentColor": "#F7DC6F",
    "backgroundColor": "#EBF5FB",
    "arrowStyle": "solid",
    "fontSize": "16px",
    "fontFamily": "Arial, sans-serif",
    "domain": "healthcare"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Future Enhancements

Potential improvements:
1. Allow users to override style config manually
2. Support custom domain keyword mappings
3. Add more theme options
4. Support gradient colors
5. Add animation styles
6. Export style configs for reuse

## Testing

To test the system:
1. Create a project with a domain-specific prompt (e.g., "Build a healthcare patient management system")
2. Generate diagrams
3. Verify consistent styling across all diagrams
4. Check that same prompt produces same styles
5. Verify domain-specific colors are applied

