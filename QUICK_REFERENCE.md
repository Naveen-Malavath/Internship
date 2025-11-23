# Quick Reference: Mermaid Fixes & Feedback System

## ✅ **What Was Fixed**

### **Parsing Errors - ALL RESOLVED**
| Error | Root Cause | Solution | Layer |
|-------|-----------|----------|-------|
| `User:::userEntity {` | Triple colon with brace | Convert to class statement | Layer 1 |
| `class Node1,Node2 cls` | Comma-separated syntax | Split into individual statements | Layer 2 |
| `stroke:#197` | Incomplete hex color | Pad to 6 digits: `#197197` | Layer 4 |
| `["(\"Label\")"]` | Escaped quotes | Remove backslashes, use single quotes | Layer 6 |
| `classDiagram +React` | Orphaned member | Remove members without class | Layer 8 |

### **Readability - IMPROVED**
- **Font sizes:** 16-18px → **18-20px** (+12-20%)
- **Spacing:** 50-60px → **60-70px** (+17-20%)
- **Scaling:** LLD diagrams now scale up to **200%**

### **Feedback System - FIXED**
- ✅ Added missing `projectTitle` field
- ✅ Enhanced logging for debugging
- ✅ Diagrams now update immediately after feedback

---

## 🎯 **How to Use Feedback System**

### **Step 1: Open Diagram**
Navigate to workspace view and select a diagram (HLD/LLD/DBD)

### **Step 2: Click Feedback Button**
Look for the feedback chatbot component below the diagram

### **Step 3: Enter Your Feedback**
Examples of good feedback:
```
✅ "Add microservices architecture pattern"
✅ "Show database connection pooling"
✅ "Include authentication flow"
✅ "Make the diagram more detailed"
✅ "Simplify the backend services layer"
```

### **Step 4: Submit & Wait**
- Click "Submit" button
- Wait 10-30 seconds for AI to regenerate
- New diagram will appear automatically
- All 8 protection layers applied automatically

### **Step 5: Verify Changes**
Check browser console for:
```
🎨 Visualization regenerated from feedback
🔄 Updating mermaid input with regenerated content
✅ Visualization update complete
```

---

## 🔍 **Debugging Tips**

### **If Diagram Doesn't Update:**

1. **Check Browser Console** (F12)
   - Look for: `🎨 Visualization regenerated from feedback`
   - If missing → feedback not reaching backend

2. **Check Network Tab** (F12 → Network)
   - Look for: `POST /api/feedback/regenerate`
   - Status should be: **200 OK**
   - Response should have: `regeneratedContent.mermaid`

3. **Check Backend Logs**
   - Look for: `[FeedbackService] Regenerating content`
   - Look for: `[Agent3] Generating mermaid diagram`

4. **Common Issues:**
   - ❌ No `projectId` → Check workspace view props
   - ❌ Empty `features` or `stories` → Backend will use minimal data
   - ❌ Timeout → Increase `REGENERATION_TIMEOUT` in feedback component

### **If Parse Errors Still Occur:**

1. **Check Console Logs:**
   ```
   🛡️ Starting 8-layer Mermaid sanitization...
   ✅ All 8 protection layers applied successfully
   📊 Input lines: X → Output lines: Y
   ```

2. **If Layer Logs Missing:**
   - Sanitization didn't run
   - Check `setMermaidInput()` is called
   - Check `renderMermaid()` is triggered

3. **If Parse Error After Sanitization:**
   - Copy error message
   - Check which line number fails
   - Add new pattern to appropriate layer

---

## 📊 **Layer Protection Map**

```
Input Mermaid Diagram
        ↓
Layer 1: Fix triple colon syntax (:::)
        ↓
Layer 2: Split comma-separated classes
        ↓
Layer 3: Complete truncated CSS
        ↓
Layer 4: Fix incomplete hex colors ⭐⭐⭐
        ↓
Layer 5: Fix erDiagram formatting
        ↓
Layer 6: Fix quotes & escapes ⭐⭐
        ↓
Layer 7: Quote all node labels
        ↓
Layer 8: Line-by-line validation ⭐⭐
        ↓
Clean Mermaid Diagram
        ↓
Mermaid.js Parser
        ↓
Rendered SVG
```

---

## 🛠️ **Adding New Protection Layers**

If you encounter a new parse error:

1. **Identify the pattern** in error message
2. **Create regex pattern** to match it
3. **Add to appropriate layer** (or create Layer 9)
4. **Add console.log** for debugging
5. **Test with example** that caused error

Example:
```typescript
// Layer 9: Fix new issue
normalised = normalised.replace(/pattern/g, (match, group1) => {
  console.log(`[workspace-view] 🔧 Layer 9: Fixed issue`);
  return fixedVersion;
});
```

---

## 📁 **Files to Know**

### **Frontend:**
- `workspace-view.component.ts` - Main sanitization logic (8 layers)
- `diagram-data.service.ts` - Diagram generation (fixed comma issue)
- `feedback-chatbot.component.ts` - Feedback UI & submission
- `feedback.service.ts` - HTTP client for feedback API

### **Backend:**
- `routers/feedback.py` - Feedback endpoints
- `services/feedback_service.py` - Regeneration orchestration
- `services/agent3.py` - Mermaid diagram generation

---

## 🎨 **Customizing Font Sizes**

In `workspace-view.component.ts`, around line 438:

```typescript
// Current settings:
const baseFontSize = isLLD ? '20px' : isDBD ? '18px' : '18px';
const nodeSpacing = isLLD ? 70 : isDBD ? 55 : 60;

// To make even larger:
const baseFontSize = isLLD ? '22px' : isDBD ? '20px' : '20px';
const nodeSpacing = isLLD ? 80 : isDBD ? 65 : 70;
```

---

## 🚦 **Health Check**

Run these checks to verify everything works:

### ✅ **Sanitization Test:**
1. Create diagram with: `classDef test fill:#19`
2. Check console: Should see Layer 4 padding `#19` to `#191919`
3. Diagram should render without errors

### ✅ **Feedback Test:**
1. Open any diagram
2. Enter feedback: "Add more detail"
3. Click Submit
4. Wait for response
5. Verify diagram updates

### ✅ **Font Size Test:**
1. Open HLD diagram
2. Check node labels are readable
3. Should be at least 18px font
4. Zoom should work smoothly

---

## 📞 **Support**

If issues persist:
1. Copy full error message from console
2. Copy network request/response from DevTools
3. Check backend logs for errors
4. Check `MERMAID_FIXES_SUMMARY.md` for detailed explanations

---

**Quick Start:** Everything should work automatically! Just use the feedback button and the system will handle all parsing fixes.

