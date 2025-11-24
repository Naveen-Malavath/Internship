# How to Test the Diagram Fixes

## Quick Test Guide

### 1. Start the Servers

Make sure both backend and frontend are running:

**Backend:**
```powershell
cd autoagents-backend
.\start_backend.ps1
```

**Frontend:**
```powershell
cd autoagents-frontend
npm start
```

### 2. Access the Application

Open your browser and navigate to: `http://localhost:4200`

### 3. Test LLD (Low-Level Design) Diagram

1. Create a new project or open an existing one
2. Add some features (e.g., "User Authentication", "Payment Processing", "Order Management")
3. Navigate to the workspace view
4. Click the **diagram type dropdown** button
5. Select **"LLD - Low Level Design"**
6. **Expected Result:**
   - Diagram should render successfully without parse errors
   - Should show classes/services with methods and relationships
   - If backend diagram fails, fallback diagram appears automatically

### 4. Test DBD (Database Design) Diagram

1. In the same project workspace
2. Click the **diagram type dropdown** button
3. Select **"DBD - Database Design"**
4. **Expected Result:**
   - Diagram should render successfully without parse errors
   - Should show database entities with fields and relationships
   - Entity definitions should be complete with proper braces
   - If backend diagram fails, fallback diagram appears automatically

### 5. Test Light/Dark Theme Toggle

1. While viewing any diagram (HLD, LLD, or DBD)
2. Click the **"Switch to light mode"** button (or "Switch to dark mode")
3. **Expected Result:**
   - Theme should toggle smoothly
   - Light theme should have good contrast (not too bright!)
   - Diagrams should remain readable in both themes
   - Background should be: darker tones, not bright white

### 6. Test Fallback Mechanism

To specifically test the fallback mechanism, you can:

1. **Option A: Force Backend Error**
   - Temporarily stop the backend server
   - Try to regenerate a diagram
   - Frontend should fall back to predefined diagram

2. **Option B: Test with Existing Data**
   - Load a project that might have invalid backend diagrams
   - The frontend should detect errors and use fallback diagrams automatically

### 7. Verify Error Messages

If a backend diagram does fail:

**Expected Behavior:**
- Error message: "Diagram invalid — [specific error]. Using fallback diagram."
- Fallback diagram appears within ~100ms
- No blank screen or stuck state
- User can continue working normally

**NOT Expected:**
- Error message: "Parse error on line 10: ...tamp updated_at } uuid user_"
- Error message: "Parse error on line 2: classDiagram +String +Map"
- Blank diagram area with no recovery

## What to Look For

### ✅ Success Indicators

1. **LLD Diagrams:**
   - Shows classes with proper structure
   - All class members inside `{ }` braces
   - No members appearing after `classDiagram` keyword
   - Clear relationships between classes

2. **DBD Diagrams:**
   - Shows entities with proper structure
   - All fields inside `{ }` braces
   - Entity relationships clearly visible
   - No fields appearing outside entity blocks

3. **Light Theme:**
   - Background is darker tones (not bright white)
   - Text is clearly readable
   - Diagram elements have good contrast

4. **Fallback Mechanism:**
   - Automatic recovery when errors occur
   - Seamless transition to fallback diagram
   - User is informed but not blocked

### ❌ Failure Indicators

1. **Parse Errors:**
   - "Parse error on line X" messages
   - Diagram fails to render
   - No automatic recovery

2. **Bright Light Theme:**
   - Blinding white/light blue background
   - Poor contrast with diagram elements
   - Hard to read text

3. **No Fallback:**
   - Stuck on error message
   - Blank diagram area
   - User must reload page to continue

## Browser Console

To see detailed logs:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for messages starting with:
   - `[workspace] VALIDATION` - Shows validation results
   - `[workspace] VALIDATION render failed` - Shows when fallback triggers
   - `[workspace] VALIDATION attempting fallback` - Confirms fallback is working

## Testing Different Scenarios

### Scenario 1: Fresh Project with Minimal Data
- Create new project
- Add 1-2 features only
- Test all diagram types
- **Expected:** All diagrams work, show appropriate content for minimal data

### Scenario 2: Rich Project with Many Features
- Create project with 5+ features
- Add multiple user stories
- Test all diagram types
- **Expected:** Diagrams show comprehensive architecture

### Scenario 3: Backend Unavailable
- Stop backend server
- Try to generate diagrams
- **Expected:** Fallback diagrams appear

### Scenario 4: Theme Switching
- View each diagram type
- Toggle light/dark mode for each
- **Expected:** All diagrams readable in both themes

## Troubleshooting

### Issue: Diagrams Still Show Parse Errors

**Solution:**
1. Clear browser cache
2. Hard refresh (Ctrl+Shift+R)
3. Check that both servers are running latest code
4. Restart both backend and frontend servers

### Issue: Light Theme Still Too Bright

**Solution:**
1. Make sure you've restarted the frontend dev server
2. Clear browser cache
3. Check that the SCSS file changes were compiled

### Issue: No Fallback Diagram Appears

**Solution:**
1. Check browser console for errors
2. Verify frontend code was updated correctly
3. Ensure the builders/emitters are properly imported

## Contact

If you encounter any issues or have questions:
- Check the `DIAGRAM_FIXES_SUMMARY.md` for technical details
- Review the browser console logs
- Verify all code changes were applied correctly

---

**Happy Testing! 🎉**

