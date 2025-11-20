# Backend-Frontend Connectivity Diagnostic

## Issues Found

### 1. ✅ CORS Configuration - WORKING
- Backend allows `http://localhost:4200` and `http://127.0.0.1:4200`
- CORS headers are properly set
- Preflight OPTIONS requests are handled correctly

### 2. ✅ API Endpoints - WORKING
- Backend is running on port 8000
- API documentation available at `/docs`
- Root endpoint responds correctly

### 3. ⚠️ Potential Issues to Check

#### Issue A: Error Handling in Frontend
The frontend has error handling that falls back to static templates, which might mask connectivity issues.

**Location**: `workspace-view.component.ts:402-410`
```typescript
error: (err) => {
  console.error(`[workspace-view] Failed to fetch designs:`, err);
  this.isLoadingDesigns = false;
  
  // Fallback to static template on error
  console.log(`[workspace-view] Falling back to static template for ${type}`);
  this.loadPredefinedDiagram(type);
}
```

**Problem**: If backend is unreachable, user sees static template instead of error message.

#### Issue B: Missing Error Display
The `project-design-view` component has error handling but might not display errors prominently.

**Location**: `project-design-view.component.ts:62-72`
```typescript
error: (err) => {
  this.isLoadingDesigns = false;
  if (err.status === 404) {
    this.hasNoDesigns = true;
    this.error = null;
  } else {
    this.error = err.message || 'Failed to load designs';
  }
}
```

#### Issue C: Style Config Not Applied
The `mermaidStyleConfig` might not be properly passed from `project-design-view` to `workspace-view`.

**Check**: Verify `mermaidStyleConfig` is being passed correctly in the template.

## Testing Checklist

### Backend Tests
- [ ] Test GET `/projects/{project_id}/designs` endpoint
- [ ] Test POST `/projects/{project_id}/designs/generate` endpoint
- [ ] Verify MongoDB connection
- [ ] Check if designs are being saved correctly

### Frontend Tests
- [ ] Verify `environment.apiUrl` is correct
- [ ] Test API calls from browser console
- [ ] Check browser network tab for failed requests
- [ ] Verify Mermaid rendering works with sample diagrams
- [ ] Check if style config is being applied

### Integration Tests
- [ ] Create a test project
- [ ] Generate designs
- [ ] Verify designs appear in frontend
- [ ] Check if switching between HLD/LLD/DBD works
- [ ] Verify live preview updates correctly

## Diagnostic Commands

### Test Backend API
```bash
# Test root endpoint
curl http://localhost:8000/

# Test designs endpoint (replace PROJECT_ID)
curl http://localhost:8000/projects/PROJECT_ID/designs

# Test CORS
curl -X OPTIONS -H "Origin: http://localhost:4200" \
  -H "Access-Control-Request-Method: GET" \
  http://localhost:8000/projects/PROJECT_ID/designs -v
```

### Test Frontend
1. Open browser console (F12)
2. Check Network tab for API calls
3. Look for errors in Console tab
4. Test API call manually:
```javascript
fetch('http://localhost:8000/projects/PROJECT_ID/designs')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

## Common Issues and Solutions

### Issue 1: CORS Errors
**Symptoms**: Browser console shows CORS errors
**Solution**: Verify backend CORS configuration allows frontend origin

### Issue 2: 404 Errors
**Symptoms**: "No designs found" error
**Solution**: Ensure designs have been generated for the project

### Issue 3: Network Errors
**Symptoms**: "Failed to fetch" errors
**Solution**: 
- Check if backend is running
- Verify `environment.apiUrl` is correct
- Check firewall/network settings

### Issue 4: Mermaid Render Errors
**Symptoms**: Diagrams don't render, parse errors
**Solution**: 
- Check Mermaid syntax in generated diagrams
- Verify `classDef` is only used for supported diagram types
- Check browser console for specific error messages

### Issue 5: Styling Not Applied
**Symptoms**: Diagrams render but without custom colors/themes
**Solution**:
- Verify `style_config` is returned from backend
- Check if `mermaidStyleConfig` is passed to `workspace-view`
- Verify `MermaidStyleService.generateMermaidConfig` is called

