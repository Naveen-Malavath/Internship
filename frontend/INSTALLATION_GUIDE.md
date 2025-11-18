# 🎯 Complete Installation Guide - Step by Step

Follow this guide exactly to get your ChatGPT-style chatbot running.

---

## ✅ **STEP 1: Install Node.js**

### **1.1 Download Node.js**

1. Open your web browser
2. Go to: **https://nodejs.org/**
3. You'll see two big green buttons
4. Click on **"LTS"** (Long Term Support) - currently v20.x.x
5. The file will download (about 30MB)
6. File name will be like: `node-v20.x.x-x64.msi`

### **1.2 Install Node.js**

1. **Find** the downloaded file (usually in Downloads folder)
2. **Double-click** the `.msi` file
3. **Click** "Next" on the welcome screen
4. **Accept** the license agreement
5. **Keep** the default installation path:
   ```
   C:\Program Files\nodejs\
   ```
6. **Important:** On the "Custom Setup" page, keep everything checked:
   - ✅ Node.js runtime
   - ✅ npm package manager
   - ✅ Online documentation shortcuts
   - ✅ Add to PATH

7. **Important:** On the "Tools for Native Modules" page:
   - ✅ **Check the box** "Automatically install the necessary tools"
   - This installs Python and Visual Studio Build Tools

8. **Click** "Next", then "Install"
9. **Wait** 2-3 minutes for installation
10. **Click** "Finish"

### **1.3 Additional Tools Installation**

After clicking Finish, a **PowerShell window** will open:
- It will install Python and Visual Studio Build Tools
- This takes 5-10 minutes
- **Wait for it to complete**
- Press any key when it says "Press any key to continue"
- The window will close automatically

### **1.4 Verify Installation**

1. **Close** any open terminals/PowerShell windows
2. **Open** a NEW PowerShell or Command Prompt:
   - Press `Win + X`
   - Select "Windows PowerShell" or "Terminal"

3. **Type** these commands:

```powershell
node --version
```

**Expected output:**
```
v20.11.0
```

```powershell
npm --version
```

**Expected output:**
```
10.2.4
```

✅ **If you see version numbers, Node.js is installed correctly!**

❌ **If you see "not recognized" error:**
- Restart your computer
- Try again
- If still not working, reinstall Node.js

---

## ✅ **STEP 2: Navigate to Project**

Open PowerShell/Terminal and navigate to your project:

```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship
```

Verify you're in the right place:

```powershell
dir
```

**You should see:**
```
package.json
angular.json
src/
README.md
... etc
```

---

## ✅ **STEP 3: Install Project Dependencies**

Now install all required packages:

```powershell
npm install
```

### **What to Expect:**

**Output will look like:**
```
npm WARN deprecated inflight@1.0.6: This module is not supported...
npm WARN deprecated rimraf@3.0.2: Rimraf versions prior to v4...

added 1247 packages, and audited 1248 packages in 2m

127 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

### **Timeline:**
- **Duration:** 2-5 minutes (depending on internet speed)
- **Download size:** ~200-300 MB
- **Creates:** `node_modules` folder with 1200+ packages

### **What's Being Installed:**
- ✅ Angular framework (v17)
- ✅ TypeScript compiler (v5.2)
- ✅ RxJS for reactive programming
- ✅ Marked.js for markdown
- ✅ Highlight.js for code highlighting
- ✅ And 1200+ other dependencies

### **Troubleshooting:**

**If you get errors:**

1. **"Cannot find module" error:**
   ```powershell
   npm cache clean --force
   npm install
   ```

2. **Permission errors:**
   - Run PowerShell as Administrator
   - Right-click PowerShell → "Run as Administrator"

3. **Network timeout:**
   ```powershell
   npm config set registry https://registry.npmjs.org/
   npm install
   ```

4. **Still having issues:**
   ```powershell
   Remove-Item -Recurse -Force node_modules
   Remove-Item package-lock.json
   npm install
   ```

---

## ✅ **STEP 4: Start the Application**

Start the development server:

```powershell
npm start
```

### **What to Expect:**

**Initial compilation (takes 10-30 seconds):**
```
Initial chunk files | Names         |  Raw Size
main.js             | main          |   2.50 MB
polyfills.js        | polyfills     |  90.00 kB
styles.css          | styles        |  10.00 kB

                    | Initial Total |   2.60 MB

Build at: 2025-11-04T10:30:00.000Z - Hash: 1234567890abcdef
```

**Server starts:**
```
** Angular Live Development Server is listening on localhost:4200,
   open your browser on http://localhost:4200/ **

✔ Compiled successfully.
```

**What's happening:**
1. TypeScript → JavaScript compilation
2. CSS processing
3. File bundling
4. Development server starts
5. Watches for file changes

### **Important Notes:**

- ⚠️ **DO NOT close this terminal window** - server runs here
- ✅ Server runs on: `http://localhost:4200`
- ✅ Auto-reloads when you edit files
- ✅ Press `Ctrl+C` to stop server

---

## ✅ **STEP 5: Open in Browser**

### **Option 1: Automatic**
- Browser should open automatically
- Goes to `http://localhost:4200`

### **Option 2: Manual**
1. Open your web browser (Chrome, Firefox, Edge)
2. In the address bar, type:
   ```
   http://localhost:4200
   ```
3. Press Enter

### **First Load:**
- Takes 2-3 seconds
- You'll see the page load

---

## 🎉 **STEP 6: See Your ChatGPT-Style Chatbot!**

### **What You Should See:**

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  SIDEBAR (Left - Gray Background)    MAIN AREA (Right - White) │
│  ──────────────────────────────────  ────────────────────────── │
│                                                                 │
│  ┌──────────────────────────────┐                              │
│  │ [+] New chat         [≡]     │          🤖                  │
│  └──────────────────────────────┘                              │
│                                      How can I help you today? │
│  Conversations:                                                 │
│  (No conversations yet)              ┌────────┐  ┌────────┐    │
│                                      │ 💻     │  │ 🎧     │    │
│                                      │ Best   │  │ Noise  │    │
│                                      │ laptop │  │ cancel │    │
│                                      └────────┘  └────────┘    │
│                                                                 │
│                                      ┌────────┐  ┌────────┐    │
│                                      │ 📚     │  │ 🎮     │    │
│  ──────────────────────────────      │ Learn  │  │ Gaming │    │
│  [🌙] Dark mode                      │ web    │  │ setup  │    │
│  [🗑️] Clear conversations            └────────┘  └────────┘    │
│                                                                 │
│                                      ┌──────────────────────┐  │
│                                      │ Message AI...     [➤]│  │
│                                      └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### **Visual Elements:**

✅ **Sidebar (Left):**
- Gray background (#f7f7f8)
- "New chat" button at top
- Empty conversation list
- Theme toggle button (moon icon)
- Clear button at bottom

✅ **Main Area (Right):**
- White background
- Robot emoji 🤖
- Large heading: "How can I help you today?"
- 4 colorful suggestion cards
- Input box at bottom with send button

---

## 🎮 **STEP 7: Test the Chatbot**

### **Test 1: Click a Suggestion**

1. **Click** on "💻 Best laptop for programming" card
2. **Watch:**
   - Card disappears
   - Your message appears (right side)
   - Loading dots appear (left side)
   - Bot responds with formatted text

**Expected Response:**
```
🛍️ Product Recommendations

I found 1 product for you:

1. MacBook Pro 16"
   Category: Electronics > Computers
   Price: $2,499
   Rating: ⭐⭐⭐⭐⭐ 4.8/5

   Professional-grade laptop with M3 Pro/Max chip, stunning 
   Liquid Retina XDR display, and all-day battery life. Perfect 
   for developers, designers, and content creators.

   🔗 View MacBook Pro 16"

💡 Need more help? Feel free to ask me about...
```

### **Test 2: Type Your Own Message**

1. **Click** in the input box at bottom
2. **Type:** "I need wireless headphones"
3. **Press** Enter or click Send button (➤)
4. **See:** Response with Sony WH-1000XM5 details

### **Test 3: Try Dark Mode**

1. **Click** the moon icon (🌙) in sidebar
2. **Watch:** 
   - Smooth color transition
   - Background turns dark gray (#212121)
   - Text turns light gray
   - Moon changes to sun icon ☀️

**Dark Mode Colors:**
- Background: Dark gray
- Text: Light gray
- Cards: Darker gray
- Accent: Green (#19c37d)

### **Test 4: Create Multiple Chats**

1. **Click** "New chat" button
2. **Type:** "Where can I learn programming?"
3. **See:** New conversation in sidebar
4. **Click** between conversations to switch

### **Test 5: Copy a Message**

1. **Hover** over a bot message
2. **Click** "Copy" button
3. **See:** "Copied!" confirmation
4. **Paste** (Ctrl+V) in Notepad to verify

---

## 📸 **Expected Output Screenshots**

### **Screenshot 1: Welcome Screen**
- Clean white/gray interface
- 4 suggestion cards
- Empty sidebar
- Input box ready

### **Screenshot 2: After First Message**
```
User: "Show me laptops"
Bot:  🛍️ Product Recommendations
      
      1. MacBook Pro 16"
      Price: $2,499
      Rating: ⭐⭐⭐⭐⭐ 4.8/5
      
      [Full description and link]
```

### **Screenshot 3: Conversation List**
```
Sidebar shows:
📝 Show me laptops
   Today
   
📝 Learn programming
   Today
```

### **Screenshot 4: Dark Mode**
- Dark backgrounds
- Light text
- Green accents
- Same functionality

---

## 🔍 **Verification Checklist**

After following all steps, verify:

### **✅ Installation:**
- [ ] Node.js installed (check: `node --version`)
- [ ] npm installed (check: `npm --version`)
- [ ] Dependencies installed (check: `node_modules` folder exists)

### **✅ Server Running:**
- [ ] `npm start` runs without errors
- [ ] Shows "Compiled successfully"
- [ ] No red error messages
- [ ] Terminal stays open

### **✅ Browser Display:**
- [ ] Page loads at http://localhost:4200
- [ ] No blank screen
- [ ] Sidebar visible on left
- [ ] Welcome message visible
- [ ] 4 suggestion cards visible
- [ ] Input box visible at bottom

### **✅ Functionality:**
- [ ] Can click suggestion cards
- [ ] Bot responds to messages
- [ ] Can type and send messages
- [ ] Markdown formatting works
- [ ] Links are clickable
- [ ] Can create new chats
- [ ] Can switch between chats
- [ ] Dark mode toggle works
- [ ] Copy button works

### **✅ Performance:**
- [ ] Page loads in < 3 seconds
- [ ] Bot responds in < 1 second
- [ ] Smooth animations
- [ ] No console errors (Press F12 to check)

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: "npm is not recognized"**
**Cause:** Node.js not installed or not in PATH

**Solution:**
1. Reinstall Node.js
2. Restart computer
3. Try again

### **Issue 2: Port 4200 already in use**
**Error:** `Port 4200 is already in use`

**Solution:**
```powershell
# Use different port
npm start -- --port 4300

# Or kill the process
netstat -ano | findstr :4200
taskkill /PID <PID_NUMBER> /F
```

### **Issue 3: Blank white screen**
**Cause:** JavaScript errors

**Solution:**
1. Press F12 to open DevTools
2. Check Console tab for errors
3. Hard refresh: Ctrl+Shift+R
4. Clear cache and reload

### **Issue 4: Styles not loading**
**Cause:** CSS not compiled

**Solution:**
```powershell
# Stop server (Ctrl+C)
Remove-Item -Recurse -Force .angular
npm start
```

### **Issue 5: Module not found**
**Error:** `Cannot find module '@angular/core'`

**Solution:**
```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npm start
```

---

## 📊 **Performance Metrics**

Expected performance:

| Metric | Expected Value |
|--------|---------------|
| Initial Load | 2-3 seconds |
| Bot Response | < 500ms |
| Conversation Switch | Instant |
| Theme Toggle | Instant |
| Memory Usage | < 100MB |
| CPU Usage | < 5% idle |

---

## 🎯 **Next Steps After Installation**

Once everything is working:

### **1. Explore Features**
- Try all suggestion prompts
- Test dark mode
- Create multiple conversations
- Copy messages
- Test markdown formatting

### **2. Customize**
- Add your own products
- Add your own websites
- Change colors
- Modify suggestion prompts

### **3. Learn the Code**
- Open project in VS Code
- Explore `src/app/` folder
- Read component files
- Understand services

### **4. Deploy**
- Build for production: `npm run build`
- Deploy to Netlify, Vercel, etc.
- Share with others

---

## 📞 **Need More Help?**

### **Resources:**
- **README.md** - Complete documentation
- **FEATURES.md** - Feature details
- **SETUP_GUIDE.md** - Advanced setup
- **CHANGELOG.md** - Version history

### **Check:**
1. Console for errors (F12)
2. Network tab for failed requests
3. Terminal for error messages

### **Common Commands:**

```powershell
# Start server
npm start

# Stop server
Ctrl + C

# Reinstall everything
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install

# Build for production
npm run build

# Clear Angular cache
Remove-Item -Recurse -Force .angular
```

---

## ✅ **Success Indicators**

You'll know it's working when:

1. ✅ Terminal shows "Compiled successfully"
2. ✅ Browser opens to http://localhost:4200
3. ✅ You see the welcome screen
4. ✅ Clicking suggestions gets responses
5. ✅ Dark mode toggle works
6. ✅ No errors in browser console (F12)

---

## 🎉 **Congratulations!**

If you can:
- ✅ See the welcome screen
- ✅ Send a message
- ✅ Get a formatted response
- ✅ Toggle dark mode

**Your ChatGPT-style chatbot is working perfectly! 🚀**

Enjoy exploring your AI Shopping Assistant!

---

**Questions? Check the troubleshooting section or README.md**


