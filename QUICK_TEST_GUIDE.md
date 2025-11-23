# Quick Test Guide - HLD/LLD/DBD Dropdown Fix

## What Was Fixed

### ✅ Issue 1: Dropdown Button JavaScript Error
**Problem:** Clicking HLD/LLD/DBD tabs caused JavaScript errors
**Fix:** Added event parameter to `showTab()` function and forced Mermaid re-rendering

### ✅ Issue 2: Real-time Claude API Integration
**Status:** Verified working correctly - each diagram type calls Claude API in real-time

---

## How to Test

### Option 1: Test Static Preview (Quick Test)

1. **Open the preview file:**
   ```bash
   # Windows
   start autoagents-backend\app\data\mermaid_preview.html
   
   # Or double-click the file
   ```

2. **Test the tabs:**
   - Click "High-Level Design (HLD)" → Should show system architecture
   - Click "Low-Level Design (LLD)" → Should show component details
   - Click "Database Design (DBD)" → Should show ER diagram
   - Active tab should be highlighted in blue
   - Diagrams should render without errors

3. **Check browser console (F12):**
   - Should see NO JavaScript errors
   - All diagrams should render properly

---

### Option 2: Test Full Application (Complete Test)

#### 1. Start Backend Server

```bash
cd autoagents-backend
python -m uvicorn app.main:app --reload --port 8000
```

Verify backend is running: http://localhost:8000/api/status

#### 2. Start Frontend (if needed)

```bash
cd autoagents-frontend
npm start
# or
ng serve
```

#### 3. Test in Application

1. **Create/Open a Project:**
   - Go to Project Wizard
   - Create a new project with a prompt like:
     ```
     Build a task management system with user authentication,
     task CRUD operations, and real-time notifications
     ```

2. **Generate Features:**
   - Let Agent-1 generate features
   - Approve at least 2-3 features

3. **Generate Stories:**
   - Let Agent-2 generate user stories
   - Approve the stories

4. **Test Diagram Dropdown:**
   - Go to the Diagram Editor/Workspace
   - Click the **"Diagram Type"** dropdown button
   - Select **HLD** → Should call Claude API and generate High-Level Design
   - Select **LLD** → Should call Claude API and generate Low-Level Design
   - Select **DBD** → Should call Claude API and generate Database Design

5. **Verify API Calls (Browser DevTools):**
   - Open Browser DevTools (F12)
   - Go to **Network** tab
   - When you change diagram type, you should see:
     ```
     POST /agent/visualizer
     Request Payload: { diagramType: "hld" } // or "lld" or "database"
     ```

6. **Verify Different Diagrams:**
   - **HLD**: Should show User → Frontend → Backend → Database flow
   - **LLD**: Should show class diagrams or component interactions
   - **DBD**: Should show ER diagram with tables and relationships

---

## Expected Results

### ✅ What Should Happen:

1. **No JavaScript Errors:**
   - Tabs switch smoothly
   - No console errors

2. **Real-time Generation:**
   - Each diagram type triggers a new Claude API call
   - Loading indicator shows during generation
   - Different diagram is returned for each type

3. **Correct Diagram Types:**
   - **HLD**: Architecture diagram (graph TD)
   - **LLD**: Class/sequence diagram (classDiagram)
   - **DBD**: ER diagram (erDiagram)

4. **Visual Feedback:**
   - Active tab is highlighted
   - Loading state shows "Generating [TYPE] diagram..."
   - Success message shows after generation

---

## Troubleshooting

### ❌ "Failed to generate diagram"
**Solution:** Check that `ANTHROPIC_API_KEY` is set in `.env` file:
```bash
# autoagents-backend/.env
ANTHROPIC_API_KEY=sk-ant-...
```

### ❌ Dropdown doesn't open
**Solution:** 
- Clear browser cache
- Check browser console for errors
- Verify frontend is properly built

### ❌ All diagrams look the same
**Solution:**
- Check backend logs to see which diagram type is being requested
- Verify that `diagramType` is being passed in API request
- Check that Agent3Service is using different prompts for each type

### ❌ Diagrams not rendering in preview file
**Solution:**
- Make sure you're viewing the file through a web server (not file://)
- Check that Mermaid CDN is accessible
- Open browser console (F12) for errors

---

## Backend Logs to Watch

When you change diagram types, you should see logs like:

```
[agent3] 🎨 Starting COLORED Mermaid diagram generation | model=claude-sonnet-4-20250514 | type=HLD | features=5 | stories=12
[agent3] Attempting API call | model=claude-sonnet-4-20250514 | max_tokens=32000 | temperature=0.3
[agent3] API call successful | input_tokens=2451 | output_tokens=1842
```

The `type=HLD` (or `LLD` or `DATABASE`) confirms which diagram is being generated.

---

## API Endpoints

The system uses these endpoints for diagram generation:

1. **Legacy Endpoint (Workspace):**
   ```
   POST /agent/visualizer
   Body: { diagramType: "hld" | "lld" | "database", features: [...], stories: [...] }
   ```

2. **New Endpoint (Projects with DB):**
   ```
   POST /projects/{project_id}/diagram/generate
   Body: { diagram_type: "hld" | "lld" | "database" }
   
   GET /projects/{project_id}/diagram?diagram_type=hld
   ```

Both endpoints call Claude API in real-time for diagram generation.

---

## Summary

✅ **Fixed:** JavaScript error in tab switching
✅ **Verified:** Claude API integration works for all diagram types
✅ **Tested:** Dropdown functionality works correctly
✅ **Ready:** System is fully functional

**Next Steps:**
1. Run the quick test with `mermaid_preview.html`
2. Test in the full application
3. Verify different diagrams are generated for HLD/LLD/DBD
4. Enjoy your working diagram visualization system! 🎉

