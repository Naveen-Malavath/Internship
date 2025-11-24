# Mermaid AST Refactor - Complete Implementation

## Overview
Replaced free-text Mermaid generation with a strict, type-safe AST → emitter pipeline for HLD, LLD, and DBD diagrams.

## Architecture Changes

### 1. AST Type System (`ast.ts`)
- Defined strict interfaces for all diagram types
- Type-safe nodes, edges, classes, members, entities, fields, and relationships
- No room for invalid structures at compile time

### 2. Deterministic Emitters (`emitter.ts`)
- `emitHLD()`: Flowchart with sorted nodes/edges, grouped subgraphs
- `emitLLD()`: classDiagram with members ONLY inside class blocks
- `emitDBD()`: erDiagram with no visibility tokens, balanced braces
- All output is sorted alphabetically for deterministic results

### 3. Safe Builders (`builders.ts`)
- `buildHLD()`: Maps features to system architecture with logical grouping
- `buildLLD()`: Creates service classes (AuthService, PaymentService, etc.) with methods
- `buildDBD()`: Generates core entities (USER, ACCOUNT, TRANSACTION) with proper types
- All names sanitized (no `+`/`-`/`#` prefixes)
- All members guaranteed to be inside proper blocks

### 4. Sanitizer & Validator (`mermaid-lint.ts`)
- `stripBomAndZwsp()`: Removes BOM (U+FEFF) and zero-width spaces
- `normalizeMermaid()`: Single init line, collapsed blanks
- `validateWithMermaid()`: Returns `{ ok: true }` or `{ ok: false, message, line }`
- No "parse error" wording - uses "Diagram invalid — {reason}"

### 5. Integration (`workspace-view.component.ts`)
- Replaced predefined diagram logic with AST builders
- Flow: buildXXX() → emitXXX() → stripBomAndZwsp() → normalizeMermaid() → validateWithMermaid()
- If validation fails: show error, do NOT render
- If validation succeeds: render SVG
- No spinners, no "fallback" text, no "parse error" messages

### 6. Agent-3 Interception (`app.ts`)
- For LLD/DBD: ignore LLM text, use AST builders instead
- For HLD: use LLM response (already stable)
- Validate all generated diagrams before setting

## Key Fixes

### Bug: Top-level `+String` / `+Object`
**Before:**
```
classDiagram
    +String
    +Object
```

**After:**
```
classDiagram
  class AppService {
    +config: Object
    +name: String
  }
```

### Bug: Top-level `-routingEngine` / `+authenticateRequest`
**Before:**
```
classDiagram
    -routingEngine
    +authenticateRequest
```

**After:**
```
classDiagram
  class RouterService {
    -routingEngine: Engine
    +authenticateRequest(): boolean
  }
```

### Bug: Unbalanced Braces
**Solution:** Emitters programmatically open/close braces for each class/entity. Always balanced by construction.

### Bug: BOM/ZWSP Characters
**Solution:** `stripBomAndZwsp()` removes U+FEFF and U+200B before processing.

## Tests

### `emitter.spec.ts`
- Verifies no top-level visibility tokens
- Verifies balanced braces for any number of classes/entities
- Verifies all output passes `validateWithMermaid()`
- Regression tests for all known bugs

### `builders.spec.ts`
- Verifies valid output for all diagram types
- Verifies no top-level members
- Verifies all members inside classes
- Verifies sanitization of names with `+`/`-`/`#` prefixes
- Regression tests for BOM/ZWSP handling

## Files Modified

### Created:
- `src/app/shared/mermaid/ast.ts`
- `src/app/shared/mermaid/emitter.ts`
- `src/app/shared/mermaid/builders.ts`
- `src/app/shared/mermaid/emitter.spec.ts`
- `src/app/shared/mermaid/builders.spec.ts`

### Updated:
- `src/app/shared/mermaid/mermaid-lint.ts`
- `src/app/workspace/workspace-view.component.ts`
- `src/app/app.ts`

### Unchanged (no modifications needed):
- `src/app/workspace/workspace-view.component.html`
- `src/app/workspace/workspace-view.component.scss`

## Acceptance Criteria ✅

- [x] Switching between HLD / LLD / DBD yields valid SVG every time
- [x] No UI text with words "parse error" or "fallback"
- [x] No top-level `+String`/`+Object` or `-routingEngine` lines
- [x] All members inside `class { }` blocks
- [x] Braces always balanced by construction
- [x] BOM/ZWSP stripped automatically
- [x] Validation gates rendering (only valid diagrams shown)
- [x] Deterministic output (same input → same diagram)
- [x] Comprehensive test coverage

## Usage

```typescript
// Generate diagrams programmatically
const root = buildLLD(context, stories, features);
const mermaidText = emitLLD(root);
const clean = normalizeMermaid(stripBomAndZwsp(mermaidText));
const validation = validateWithMermaid(clean);

if (validation.ok) {
  renderMermaid(clean);
} else {
  showError(`Diagram invalid — ${validation.message}`);
}
```

## Logging

All logging uses `console.debug('[workspace] VALIDATION', ...)` format. No verbose output, only when needed.

