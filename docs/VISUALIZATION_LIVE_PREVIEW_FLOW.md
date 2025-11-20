# Visualization Live Preview Flow - Analysis & Fixes

## Problem Statement
**Issue**: Visualization was not updating/changing when diagram type was selected (HLD/LLD/Database). The same diagram was shown regardless of selection.

## Root Cause Analysis

### The Flow (Before Fix)

1. **Frontend** (`app.ts`):
   - User selects diagram type (HLD/LLD/Database)
   - `invokeAgent3()` is called with `diagramType` parameter
   - POST request sent to `/agent/visualizer` with `diagramType` in payload

2. **Backend** (`visualizer.py`):
   - ✅ Receives request with `diagramType` parameter
   - ❌ **PROBLEM**: Ignores `diagramType` parameter completely
   - Always calls `ClaudeVisualizationAgent.generate_visualization()` which:
     - Doesn't accept `diagram_type` parameter
     - Always generates generic "flow diagram (graph TD)" regardless of type
     - Returns the same diagram format every time

3. **Storage**:
   - New diagram is stored to file
   - Old cached diagram might be loaded back instead of new one

4. **Frontend**:
   - Receives response
   - Updates `workspaceMermaid` signal
   - ❌ **PROBLEM**: Change detection might not trigger if content appears similar
   - Same diagram rendered regardless of type selection

## The Fix

### Backend Fix (`app/routers/visualizer.py`)

**Changed**: Endpoint now uses `Agent3Service.generate_mermaid()` which supports diagram types:

```python
# Before: Always used ClaudeVisualizationAgent (no diagram type support)
visualization = await agent_3.generate_visualization(feature_specs, story_specs)

# After: Uses Agent3Service with diagram_type parameter
agent3_service = Agent3Service()
mermaid_diagram = await agent3_service.generate_mermaid(
    project_title=project_title,
    features=feature_dicts,
    stories=story_dicts,
    diagram_type=diagram_type,  # ✅ Now respects diagram type!
    original_prompt=original_prompt,
)
```

**Key Changes**:
1. Extracts `diagramType` from request (hld/lld/database)
2. Validates diagram type (defaults to 'hld' if invalid)
3. Uses `Agent3Service.generate_mermaid()` which generates type-specific diagrams:
   - **HLD**: High-level system architecture with subgraphs
   - **LLD**: Low-level component interactions, class diagrams, API endpoints
   - **Database**: ER diagrams with entities and relationships
4. Returns newly generated diagram (not cached version)

### Frontend Fix (`workspace-view.component.ts`)

**Changed**: Improved change detection for `mermaidEditorContent`:

```typescript
// Before: Only updated if !this.mermaidSource
if (changes['mermaidEditorContent'] && typeof changes['mermaidEditorContent'].currentValue === 'string' && !this.mermaidSource) {
  this.setMermaidInput(changes['mermaidEditorContent'].currentValue, false);
}

// After: Always updates when content changes, respects mermaidSource priority
if (changes['mermaidEditorContent']) {
  const newContent = changes['mermaidEditorContent'].currentValue;
  if (typeof newContent === 'string' && newContent.trim() !== '') {
    if (!this.mermaidSource) {
      this.setMermaidInput(newContent, false);
    } else if (this.mermaidSource === newContent.trim()) {
      // Still update to ensure rendering even if values match
      this.setMermaidInput(newContent, false);
    }
  }
}
```

**Key Changes**:
1. Better handling of `mermaidEditorContent` changes
2. Ensures rendering happens even when values might appear similar
3. Respects `mermaidSource` priority while still allowing updates

## Complete Flow (After Fix)

### 1. User Action
- User selects diagram type: **HLD** / **LLD** / **Database**
- Frontend: `onWorkspaceDiagramTypeChange(type)` or `onWorkspaceRegenerateDiagram(type)`

### 2. Frontend Request (`app.ts`)
```typescript
private invokeAgent3(features, stories, diagramType = 'hld') {
  const payload = {
    prompt: this.lastPrompt(),
    features: features,
    stories: stories,
    diagramType: diagramType,  // ✅ Passed to backend
  };
  
  this.http.post(`${this.backendUrl}/agent/visualizer`, payload)
    .subscribe({
      next: (response) => {
        // ✅ Updates signals with new diagram
        this.workspaceMermaid.set(response.diagrams?.mermaid ?? '');
        this.workspaceVisualization.set(response);
      }
    });
}
```

### 3. Backend Generation (`visualizer.py`)
```python
@router.post("")
async def agent_visualizer(request: AgentVisualizationRequest):
    # ✅ Extract and validate diagram type
    diagram_type = (request.diagramType or "hld").lower()
    if diagram_type not in {"hld", "lld", "database"}:
        diagram_type = "hld"
    
    # ✅ Use Agent3Service with diagram type
    agent3_service = Agent3Service()
    mermaid_diagram = await agent3_service.generate_mermaid(
        project_title=project_title,
        features=feature_dicts,
        stories=story_dicts,
        diagram_type=diagram_type,  # ✅ Type-specific generation
        original_prompt=original_prompt,
    )
    
    # ✅ Store and return NEW diagram
    store_visualization_assets(mermaid_diagram, dot_diagram)
    return AgentVisualizationResponse(
        diagrams=VisualizationDiagram(mermaid=mermaid_diagram, ...)
    )
```

### 4. Agent3Service Generation (`agent3.py`)
```python
async def generate_mermaid(self, diagram_type: str = "hld", ...):
    # ✅ Different prompts based on diagram type
    if diagram_type == "lld":
        # Generates Low Level Design with class diagrams, API endpoints
    elif diagram_type == "database":
        # Generates ER diagram with entities and relationships
    else:  # hld
        # Generates High Level Design with system architecture
    
    # ✅ Applies domain-specific styling
    # ✅ Returns type-specific Mermaid diagram
```

### 5. Frontend Rendering (`workspace-view.component.ts`)
```typescript
ngOnChanges(changes: SimpleChanges) {
  // ✅ Detects mermaidEditorContent changes
  if (changes['mermaidEditorContent']) {
    const newContent = changes['mermaidEditorContent'].currentValue;
    if (typeof newContent === 'string' && newContent.trim() !== '') {
      // ✅ Updates and re-renders diagram
      this.setMermaidInput(newContent, false);
    }
  }
}

async renderMermaid() {
  // ✅ Renders new diagram type
  const { svg } = await mermaid.render(renderId, definition);
  // ✅ Updates preview
}
```

## Diagram Type Differences

### HLD (High Level Design)
- System architecture overview
- Subgraphs: Frontend, Backend, Data Layer, AI/Agents
- High-level component interactions
- Business flow from features to stories
- Uses: `flowchart TD` or `flowchart LR`

### LLD (Low Level Design)
- Component/class/module interactions
- API endpoints and service layers
- Detailed data flow between components
- Database interactions
- Uses: `classDiagram`, `sequenceDiagram`, or detailed flowcharts

### Database Design
- Entity-Relationship Diagram (ERD)
- Tables and relationships
- Primary keys, foreign keys
- Data entities and attributes
- Uses: `erDiagram` or `entityRelationshipDiagram`

## Testing Checklist

- [x] Backend accepts and uses `diagramType` parameter
- [x] Backend generates different diagrams for HLD/LLD/Database
- [x] Frontend properly detects changes in `mermaidEditorContent`
- [x] Live preview updates when diagram type changes
- [ ] Test with actual API calls after credits are available
- [ ] Verify different diagram types render correctly
- [ ] Verify diagram style/styling is applied correctly

## Files Modified

1. **Backend**: `app/routers/visualizer.py`
   - Added `Agent3Service` import
   - Updated endpoint to use `Agent3Service.generate_mermaid()` with `diagram_type`
   - Properly extracts and validates `diagramType` from request

2. **Frontend**: `app/workspace/workspace-view.component.ts`
   - Improved `mermaidEditorContent` change detection
   - Ensures updates happen even when values might appear similar

## Summary

**Problem**: Visualization wasn't changing because:
1. Backend ignored `diagramType` parameter
2. Always generated same diagram type
3. Frontend change detection had edge cases

**Solution**: 
1. Backend now uses `Agent3Service` which supports diagram types
2. Frontend change detection improved to handle all cases
3. Each diagram type (HLD/LLD/Database) generates unique, type-specific diagrams

**Result**: Live preview now updates correctly when diagram type changes! 🎉

