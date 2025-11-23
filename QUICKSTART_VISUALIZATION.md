# 🚀 Quick Start Guide - Architecture Visualization

## Fix the 503 Error - 2 Simple Steps!

### Step 1: Add Your Claude API Key

1. **Get API Key**: Visit https://console.anthropic.com/ and copy your API key

2. **Create .env file**: In the `autoagents-backend` folder, create a file named `.env`

3. **Add this content** (replace with YOUR actual key):

```bash
CLAUDE_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
CLAUDE_MODEL=claude-sonnet-4-20250514
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=autoagents
```

### Step 2: Restart Backend

```bash
cd autoagents-backend

# Stop backend if running (Ctrl+C)

# Restart backend
.\start_backend.ps1
```

**✅ Done!** The 503 error should be fixed.

## Testing the Dropdown Integration

### Test 1: Generate HLD (High Level Design)

1. Open http://localhost:4200
2. Create a new project with:
   - Feature: "User Authentication System"
   - Story: "As a user, I want to log in securely"
3. Approve the feature and story
4. Click **"Diagram Type: HLD"** dropdown (top of Mermaid editor)
5. Select **"HLD"**
6. Wait 3-5 seconds
7. ✅ Should see a high-level architecture diagram with:
   - User component
   - Frontend component
   - Backend component
   - Database component
   - Auth flow

### Test 2: Generate LLD (Low Level Design)

1. In the same project, click dropdown again
2. Select **"LLD"**
3. Wait 3-5 seconds
4. ✅ Should see a DIFFERENT diagram with:
   - Class diagrams or sequence diagrams
   - Component interactions
   - API endpoints
   - Service layers

### Test 3: Generate DBD (Database Design)

1. Click dropdown again
2. Select **"DBD"**
3. Wait 3-5 seconds
4. ✅ Should see an ER diagram with:
   - USERS table
   - PROJECTS table
   - FEATURES table
   - Relationships between tables

### Test 4: Different Features = Different Diagrams

1. Create a **NEW project** with different features:
   - Feature: "Payment Processing"
   - Story: "As a user, I want to pay with credit card"
2. Select **"HLD"** from dropdown
3. ✅ The diagram should be DIFFERENT from Test 1
   - Should mention payment gateway
   - Should show payment flow
   - Should have payment-specific components

## Expected Behavior

### ✅ Success Indicators

- **No 503 errors** in browser console
- **Diagrams generate in 3-5 seconds**
- **Different diagram types show different views**:
  - HLD = High-level system view
  - LLD = Detailed component view
  - DBD = Database schema view
- **Different features produce different diagrams**
- **Live preview updates automatically**

### ❌ Known Bugs (Intentional)

These bugs were added intentionally per your request:

1. **Dropdown checkmark doesn't show**: Active diagram type indicator may not display
2. **Error says "HLD" when you selected LLD/DBD**: Wrong diagram type in error messages
3. **Can't generate with only features**: Validation too strict, requires both features AND stories

## Frontend Console Output

When working correctly, you should see:

```
[app] Diagram type changed to hld | features=1 | stories=1
[app] Invoking Agent 3 to generate HLD diagram
[app] Calling Agent 3 API: http://localhost:8000/agent/visualizer | diagramType=hld
```

When API key is missing, you'll see:

```
❌ Failed to load resource: the server responded with a status of 503 (Service Unavailable)
❌ [app] Agent 3 API error for HLD: HttpErrorResponse
```

## Backend Console Output

When working correctly:

```
[visualizer] Processing request for HLD diagram
[visualizer] Generating HLD diagram with 1 features and 1 stories
[agent3] Starting COLORED Mermaid diagram generation | model=claude-sonnet-4-20250514
[agent3] API call successful | input_tokens=1234 | output_tokens=5678
[agent3] HLD diagram generation complete | length=2345 chars | has_colors=True
```

When API key is missing:

```
❌ [visualizer] Claude API key not configured - cannot generate diagrams
❌ Agent_3 is unavailable. Claude API key is not configured.
```

## Cost Estimation

Each diagram generation costs approximately:
- Input tokens: ~1,000-3,000 tokens = $0.003-$0.009
- Output tokens: ~3,000-8,000 tokens = $0.045-$0.120
- **Total per diagram: ~$0.05-$0.13**

For 10 diagrams (testing all 3 types for a few projects):
- **Estimated cost: ~$0.50-$1.30**

## Troubleshooting

### Still getting 503 errors?

**Check 1**: Verify .env file exists
```bash
cd autoagents-backend
dir .env  # Windows
ls -la .env  # Mac/Linux
```

**Check 2**: Verify API key format
- Should start with `sk-ant-api03-`
- No quotes around the key
- No extra spaces

**Check 3**: Check backend is running
- Should see: `Uvicorn running on http://0.0.0.0:8000`
- Try: http://localhost:8000 (should show JSON response)

**Check 4**: Restart backend AFTER creating .env
- The .env file is only loaded on startup
- Changes require restart

### Diagram not updating?

**Check 1**: Verify you have approved features AND stories
- Need at least 1 approved feature
- Need at least 1 approved story

**Check 2**: Check browser console for errors
- Press F12 → Console tab
- Look for red error messages

**Check 3**: Try "Regenerate Diagram" button
- Below the diagram type dropdown
- Forces a fresh generation

### Dropdown not showing?

**Check 1**: Make sure you're in workspace view
- Not in project wizard
- Should see "Mermaid Diagram" editor

**Check 2**: Scroll to the editor section
- Dropdown is in the top-right of editor panel
- Next to "Import Mermaid" button

## Video Demo (If Available)

[Record a quick video showing]:
1. Opening dropdown
2. Selecting different types
3. Seeing different diagrams generate
4. Showing they work for different features

## Next Steps

After confirming everything works:

1. **Fix the intentional bugs** (see ARCHITECTURE_VISUALIZATION_IMPLEMENTATION.md)
2. **Test with your own features** (create real projects)
3. **Export diagrams** (copy Mermaid code and use in docs)
4. **Share with team** (show them the different diagram types)

## Need Help?

- See detailed docs: `ARCHITECTURE_VISUALIZATION_IMPLEMENTATION.md`
- Setup guide: `SETUP_CLAUDE_API.md`
- API docs: https://docs.anthropic.com/
- Mermaid docs: https://mermaid.js.org/

---

**Happy Architecting! 🎨📊🚀**

