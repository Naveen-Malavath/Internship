# ⚡ Quick Reference - Commands & Expected Output

One-page reference for running your ChatGPT-style chatbot.

---

## 🎯 **Installation Commands**

### **1. Install Node.js**
```
Download: https://nodejs.org/
Install: node-v20.x.x-x64.msi
Verify: node --version
        npm --version
```

### **2. Install Dependencies**
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship
npm install
```

**Expected Output:**
```
added 1247 packages in 2m
found 0 vulnerabilities
```

### **3. Start Server**
```powershell
npm start
```

**Expected Output:**
```
✔ Compiled successfully.
** Angular Live Development Server is listening on localhost:4200 **
```

### **4. Open Browser**
```
http://localhost:4200
```

---

## 📸 **What You'll See**

### **Initial Screen:**
```
┌──────────────┬─────────────────────────────┐
│  Sidebar     │     Welcome Screen          │
│              │                             │
│ [+ New chat] │      🤖                     │
│              │ How can I help you today?   │
│ (empty)      │                             │
│              │ [💻] [🎧] [📚] [🎮]         │
│              │ (4 suggestion cards)        │
│ [🌙 Dark]    │                             │
│ [🗑️ Clear]   │ [Message input box...]  [➤] │
└──────────────┴─────────────────────────────┘
```

### **After Sending Message:**
```
User Message (Right):
┌─────────────────────────┐
│ Show me laptops      👤 │
└─────────────────────────┘

Bot Response (Left):
┌─────────────────────────────────────┐
│ 🤖                                  │
│ ## 🛍️ Product Recommendations      │
│                                     │
│ ### 1. MacBook Pro 16"             │
│ **Price:** $2,499                  │
│ **Rating:** ⭐⭐⭐⭐⭐ 4.8/5         │
│                                     │
│ Description...                      │
│                                     │
│ 🔗 View MacBook Pro 16"            │
│ [Copy] [2:30 PM]                   │
└─────────────────────────────────────┘
```

---

## 🎮 **Test Commands**

### **Test 1: Product Search**
```
Type: "I need a laptop for programming"
Expect: MacBook Pro details with price and rating
```

### **Test 2: Website Search**
```
Type: "Where can I learn web development?"
Expect: Udemy, Coursera, GitHub recommendations
```

### **Test 3: Dark Mode**
```
Click: Moon icon in sidebar
Expect: Dark gray background, light text
```

### **Test 4: New Conversation**
```
Click: "New chat" button
Expect: New empty chat, old chat in sidebar
```

### **Test 5: Copy Message**
```
Hover: Over bot message
Click: "Copy" button
Expect: "Copied!" confirmation
```

---

## 🔧 **Useful Commands**

### **Start/Stop**
```powershell
npm start                # Start server
Ctrl + C                 # Stop server
```

### **Rebuild**
```powershell
npm run build            # Production build
```

### **Troubleshooting**
```powershell
# Reinstall dependencies
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Clear cache
Remove-Item -Recurse -Force .angular

# Use different port
npm start -- --port 4300
```

### **Check Installation**
```powershell
node --version           # Should show: v20.x.x
npm --version            # Should show: 10.x.x
dir                      # Should show: package.json, src/, etc.
```

---

## 🐛 **Quick Fixes**

| Problem | Quick Fix |
|---------|-----------|
| npm not found | Install Node.js, restart terminal |
| Port in use | `npm start -- --port 4300` |
| Blank screen | Press F12, check console, hard refresh |
| No styles | Delete `.angular` folder, restart |
| Module error | Delete `node_modules`, run `npm install` |

---

## 📊 **Performance Check**

| Metric | Expected |
|--------|----------|
| Install time | 2-5 minutes |
| Compile time | 10-30 seconds |
| Page load | 2-3 seconds |
| Bot response | < 500ms |
| Memory | < 100MB |

---

## ✅ **Success Checklist**

- [ ] Node.js installed
- [ ] `npm install` completed
- [ ] `npm start` runs
- [ ] Browser opens to localhost:4200
- [ ] Welcome screen visible
- [ ] Can send messages
- [ ] Bot responds
- [ ] Dark mode works
- [ ] No console errors

---

## 🎯 **Example Queries**

```
"Show me the best laptops for programming"
"I need wireless headphones under $400"
"Where can I learn web development?"
"What are the best streaming platforms?"
"Help me find a smartwatch for fitness"
"Show me gaming consoles"
"I need a coffee maker"
"What are the best design tools?"
```

---

## 📱 **Browser Support**

✅ Chrome (latest)  
✅ Firefox (latest)  
✅ Edge (latest)  
✅ Safari (latest)  

---

## 🔗 **Important URLs**

- **App:** http://localhost:4200
- **Node.js:** https://nodejs.org/
- **Docs:** README.md, FEATURES.md

---

## 📞 **Quick Help**

**Server won't start?**
→ Check terminal for errors
→ Try `npm install` again

**Blank screen?**
→ Press F12, check console
→ Hard refresh (Ctrl+Shift+R)

**No response from bot?**
→ Check browser console
→ Restart server

---

**🚀 Quick Start: Install Node.js → `npm install` → `npm start` → Open browser**


