# Diagram Dynamic Generation Fix

## Problem

Diagrams were not being generated dynamically - users were seeing the same diagrams or cached/static templates instead of fresh, project-specific designs generated from the backend.

## Root Causes Identified

1. **Cache Not Cleared on Regeneration**: When new designs were generated via "Generate Designs" button, the cache in `workspace-view` component was not being cleared, causing it to show stale designs when switching diagram types.

2. **No Cache Invalidation Signal**: There was no mechanism to signal `workspace-view` that new designs had been generated, so it continued using cached data.

3. **Initial Load Issue**: When designs were first loaded, `workspace-view` might not fetch from backend if cache was empty but projectId was available.

## Solutions Implemented

### 1. Design Generation Key Mechanism

**Added to `project-design-view.component.ts`**:
- Added `designGenerationCounter` that increments each time designs are generated
- This counter is passed to `workspace-view` as `designGenerationKey` input
- When the key changes, `workspace-view` clears its cache and fetches fresh data

**Code Changes**:
```typescript
private designGenerationCounter = 0; // Track design generations

protected onGenerateDesigns(): void {
  // ... existing code ...
  this.designGenerationCounter++; // Increment on each generation
  // ... rest of code ...
}
```

### 2. Cache Invalidation in Workspace View

**Added to `workspace-view.component.ts`**:
- Added `@Input() designGenerationKey` to receive generation counter
- Added logic in `ngOnChanges()` to detect key changes and clear cache
- When key changes, cache is cleared and current diagram type is reloaded from backend

**Code Changes**:
```typescript
@Input() designGenerationKey: number | null = null;

ngOnChanges(changes: SimpleChanges): void {
  // Handle designGenerationKey changes - clear cache when designs are regenerated
  if (changes['designGenerationKey']) {
    const newKey = changes['designGenerationKey'].currentValue;
    const oldKey = changes['designGenerationKey'].previousValue;
    if (newKey !== null && newKey !== oldKey) {
      this.clearDesignCache();
      if (this.projectId && this.currentDiagramType) {
        this.loadDesignFromBackend(this.currentDiagramType);
      }
    }
  }
}
```

### 3. Template Update

**Updated `project-design-view.component.html`**:
- Added `[designGenerationKey]="designGenerationCounter"` binding to `workspace-view`
- This ensures the key is passed down and triggers cache invalidation

## How It Works Now

1. **User Clicks "Generate Designs"**:
   - `onGenerateDesigns()` is called
   - Backend API is called to generate new designs
   - `designGenerationCounter` is incremented
   - New designs are received and stored

2. **Design Generation Key Changes**:
   - The incremented counter is passed to `workspace-view` as `designGenerationKey`
   - `workspace-view` detects the change in `ngOnChanges()`
   - Cache is automatically cleared
   - Current diagram type is reloaded from backend with fresh data

3. **User Switches Diagram Type**:
   - `onDiagramTypeChange()` is called
   - If `projectId` exists, `loadDesignFromBackend()` is called
   - Since cache was cleared, fresh data is fetched from backend
   - New diagram is displayed

## Verification Steps

1. **Generate designs for a project**:
   - Click "Generate Designs" button
   - Check browser console for: `[project-design-view] Design generation counter: 1`
   - Check for: `[workspace-view] Design generation key changed, clearing cache`

2. **Switch diagram types**:
   - Click HLD, LLD, or DBD tabs
   - Check console for: `[workspace-view] Fetching designs from backend for project {id}`
   - Verify diagrams are different and project-specific

3. **Regenerate designs**:
   - Click "Generate Designs" again
   - Counter should increment: `Design generation counter: 2`
   - Cache should be cleared again
   - New diagrams should appear

## Debugging

### Frontend Console Logs

Look for these log messages:
- `[project-design-view] Generating designs for project {id}`
- `[project-design-view] Design generation counter: {n}`
- `[workspace-view] Design generation key changed from {old} to {new}, clearing cache`
- `[workspace-view] Fetching designs from backend for project {id}`
- `[workspace-view] Successfully fetched designs: {details}`

### Backend Logs

Look for these log messages:
- `[agent3] Generating designs for project | fingerprint={fingerprint}`
- `[agent3] Project-specific terms found in diagrams: {terms}`
- `[projects] Design generation completed | project_id={id}`

### Common Issues

1. **Still seeing old diagrams**:
   - Check if `designGenerationKey` is being passed correctly
   - Verify cache is being cleared (check console logs)
   - Check if backend is returning new designs

2. **Diagrams not loading**:
   - Check browser network tab for API calls
   - Verify projectId is correct
   - Check backend logs for errors

3. **Same diagrams for different projects**:
   - Verify backend is generating unique designs (check logs for project fingerprint)
   - Check if project-specific terms are found in diagrams
   - Verify features and stories are different between projects

## Files Modified

1. `autoagents-frontend/src/app/workspace/project-design-view/project-design-view.component.ts`
   - Added `designGenerationCounter`
   - Increment counter on design generation

2. `autoagents-frontend/src/app/workspace/workspace-view.component.ts`
   - Added `designGenerationKey` input
   - Added cache invalidation logic in `ngOnChanges()`

3. `autoagents-frontend/src/app/workspace/project-design-view/project-design-view.component.html`
   - Added `[designGenerationKey]` binding

## Testing Checklist

- [ ] Generate designs for Project A
- [ ] Switch between HLD, LLD, DBD - should show different diagrams
- [ ] Generate designs for Project B (different project)
- [ ] Verify Project B has different diagrams than Project A
- [ ] Regenerate designs for Project A
- [ ] Verify new diagrams appear (not cached old ones)
- [ ] Check console logs for cache clearing messages
- [ ] Verify backend logs show unique fingerprints for each project

