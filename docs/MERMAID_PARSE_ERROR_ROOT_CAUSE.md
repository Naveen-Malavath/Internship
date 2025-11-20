# Root Cause Analysis: Mermaid Parse Error

## Error Message
```
Parse error on line 9:
...ion Layer"]        ((WebStorefront))  
----------------------^
Expecting 'SEMI', 'NEWLINE', 'SPACE', 'EOF', 'subgraph', 'end', ...
got 'PS'
```

## Root Cause

The root cause is a **Mermaid syntax requirement that is not documented in the prompts given to the LLM (Agent 3)**.

### The Problem

1. **Mermaid Syntax Rule**: Nodes defined **inside subgraphs** MUST have an explicit **node ID** before the shape syntax.

2. **What the LLM Generates**:
   ```mermaid
   subgraph Presentation["Presentation Layer"]
       ((WebStorefront))    ❌ WRONG - Missing node ID
       ((MobileApp))        ❌ WRONG - Missing node ID
   end
   ```

3. **What Mermaid Requires**:
   ```mermaid
   subgraph Presentation["Presentation Layer"]
       WebStorefront((WebStorefront))    ✅ CORRECT - Has node ID
       MobileApp((MobileApp))            ✅ CORRECT - Has node ID
   end
   ```

### Why This Happens

1. **Prompt Gap**: The prompts to Agent 3 show shape syntax examples like:
   - `((UIName))` for circle nodes
   - `[ServiceName]` for rectangles
   - `[(DatabaseName)]` for cylinders
   
   But they **don't explain** that inside subgraphs, you must use:
   - `NodeId((Label))` format
   - Not just `((Label))` format

2. **LLM Understanding**: The LLM sees examples and generates diagrams using the simpler syntax `((Label))`, which works **outside subgraphs** but fails **inside subgraphs**.

3. **Mermaid Parser Behavior**: 
   - Outside subgraphs: `((Label))` is acceptable (Mermaid auto-generates an ID)
   - Inside subgraphs: `((Label))` is **invalid** - parser expects explicit node ID first

### Technical Details

**Mermaid's Internal Parsing**:
- When parsing a subgraph, Mermaid expects each node definition to follow: `nodeId shapeSyntax`
- The parser encounters `((` after `]` (from subgraph label) and expects a valid token
- `((` without a preceding node ID causes the parser to throw "got 'PS'" (part of `(`)

**Error Token 'PS'**:
- The parser is reading: `]        ((`
- After `]`, it expects certain tokens (SEMI, NEWLINE, etc.)
- Instead it gets `((` which starts with `P` in the token stream
- Error message shows "got 'PS'" indicating the unexpected character sequence

## Solution Applied

### 1. Backend Fix (`agent3.py` - `_fix_mermaid_syntax()`)
- **Automatically detects** nodes without IDs inside subgraphs
- **Adds node IDs** by extracting the label and creating a sanitized ID
- **Updates connections** to use node IDs instead of shape syntax
- **Logs all fixes** for debugging

### 2. Frontend Fix (`workspace-view.component.ts` - `fixMermaidSyntax()`)
- **Additional safety net** in case backend fix misses something
- **Automatic retry** after fixing parse errors
- **Error recovery** with automatic fix attempts

### 3. Prompt Enhancement (Recommended but not yet implemented)
- Add explicit instruction: "When defining nodes inside subgraphs, always use format: `NodeId((Label))` not just `((Label))`"
- Provide examples showing both incorrect and correct syntax
- Emphasize this requirement for all diagram types using subgraphs

## Prevention

To prevent this in the future, update the prompts to include:

```python
"""
CRITICAL MERMAID SYNTAX RULES:
1. Nodes inside subgraphs MUST have explicit node IDs:
   ✅ CORRECT: subgraph Layer["Layer Name"]
                  NodeId((NodeLabel))
                  ServiceId[ServiceLabel]
              end
   
   ❌ WRONG:   subgraph Layer["Layer Name"]
                  ((NodeLabel))      # Missing node ID
                  [ServiceLabel]     # Missing node ID
              end

2. Node ID format: Must be alphanumeric with underscores only
   - Good: WebStorefront, PaymentService, OrderDB
   - Bad: Web-Storefront, Payment Service, Order.DB

3. Connections must use node IDs, not shape syntax:
   ✅ CORRECT: WebStorefront --> PaymentService
   ❌ WRONG:   ((WebStorefront)) --> [PaymentService]
"""
```

## Summary

**Root Cause**: Missing explicit instruction in prompts about Mermaid's requirement for node IDs inside subgraphs.

**Impact**: All diagrams with subgraphs generate invalid syntax, causing parse errors.

**Fix**: Automatic syntax correction in backend + frontend with comprehensive error handling.

**Long-term Solution**: Enhance prompts to explicitly document this requirement.

