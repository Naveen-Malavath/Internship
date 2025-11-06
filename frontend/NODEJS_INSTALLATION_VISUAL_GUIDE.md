# 📸 Node.js Installation - Visual Step-by-Step Guide

Follow these screenshots and instructions exactly.

---

## 🌐 **STEP 1: Download Node.js**

### What to Do:
1. Open your web browser (Chrome, Firefox, Edge)
2. Type in address bar: `https://nodejs.org/`
3. Press Enter

### What You'll See:
```
┌─────────────────────────────────────────────────────┐
│  Node.js®                                          │
│                                                     │
│  ┌────────────────┐    ┌────────────────┐         │
│  │   20.11.0 LTS  │    │   21.x.x       │         │
│  │  Recommended   │    │   Current      │         │
│  │   For Most     │    │   Latest       │         │
│  │     Users      │    │   Features     │         │
│  │                │    │                │         │
│  │ [ DOWNLOAD ]   │    │ [ DOWNLOAD ]   │         │
│  └────────────────┘    └────────────────┘         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Action:
✅ **Click the LEFT button (LTS - Recommended)**

### Result:
- File downloads automatically
- File name: `node-v20.11.0-x64.msi` (or similar)
- File size: ~30 MB
- Location: Your Downloads folder

---

## 💾 **STEP 2: Run the Installer**

### What to Do:
1. Open your Downloads folder
2. Find the file: `node-v20.x.x-x64.msi`
3. Double-click the file

### What You'll See:

#### Screen 1: Welcome
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Welcome to the Node.js Setup Wizard   │
│                                         │
│  This will install Node.js on your     │
│  computer.                              │
│                                         │
│              [ Next > ]  [ Cancel ]    │
└─────────────────────────────────────────┘
```
**Action:** Click **"Next"**

---

#### Screen 2: License Agreement
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  End-User License Agreement             │
│                                         │
│  [✓] I accept the terms in the License │
│      Agreement                          │
│                                         │
│  [ < Back ]  [ Next > ]  [ Cancel ]    │
└─────────────────────────────────────────┘
```
**Action:** 
1. Check the box ✅
2. Click **"Next"**

---

#### Screen 3: Destination Folder
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Destination Folder                     │
│                                         │
│  C:\Program Files\nodejs\               │
│                      [ Change... ]      │
│                                         │
│  [ < Back ]  [ Next > ]  [ Cancel ]    │
└─────────────────────────────────────────┘
```
**Action:** 
- **DON'T change anything**
- Click **"Next"**

---

#### Screen 4: Custom Setup (IMPORTANT!)
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Custom Setup                           │
│                                         │
│  [✓] Node.js runtime                   │
│  [✓] npm package manager               │
│  [✓] Online documentation shortcuts    │
│  [✓] Add to PATH                       │
│                                         │
│  [ < Back ]  [ Next > ]  [ Cancel ]    │
└─────────────────────────────────────────┘
```
**Action:** 
- **Keep ALL boxes checked** ✅✅✅✅
- Click **"Next"**

---

#### Screen 5: Tools for Native Modules (VERY IMPORTANT!)
```
┌─────────────────────────────────────────────────┐
│  Node.js Setup                                  │
│                                                 │
│  Tools for Native Modules                      │
│                                                 │
│  [✓] Automatically install the necessary      │
│      tools. Note that this will also          │
│      install Chocolatey. The script will      │
│      pop-up in a new window after the         │
│      installation completes.                   │
│                                                 │
│  [ < Back ]  [ Next > ]  [ Cancel ]           │
└─────────────────────────────────────────────────┘
```
**Action:** 
- ✅ **CHECK THIS BOX** (Very Important!)
- Click **"Next"**

⚠️ **This is crucial! Don't skip checking this box!**

---

#### Screen 6: Ready to Install
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Ready to install Node.js               │
│                                         │
│  Click Install to begin the            │
│  installation.                          │
│                                         │
│  [ < Back ]  [ Install ]  [ Cancel ]   │
└─────────────────────────────────────────┘
```
**Action:** Click **"Install"**

---

#### Screen 7: Installing (Wait)
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Installing Node.js                     │
│                                         │
│  [████████████░░░░░░░░░░] 60%          │
│                                         │
│  Please wait while Node.js is being    │
│  installed...                           │
└─────────────────────────────────────────┘
```
**Action:** 
- **Wait patiently** (1-2 minutes)
- Don't close the window

---

#### Screen 8: Completion
```
┌─────────────────────────────────────────┐
│  Node.js Setup                          │
│                                         │
│  Completed the Node.js Setup Wizard    │
│                                         │
│  Node.js has been successfully         │
│  installed on your computer.            │
│                                         │
│              [ Finish ]                 │
└─────────────────────────────────────────┘
```
**Action:** Click **"Finish"**

---

## 🔧 **STEP 3: Additional Tools Installation**

### What Happens Next:

After clicking "Finish", a **PowerShell window** opens automatically:

```
┌─────────────────────────────────────────────────┐
│ Administrator: Windows PowerShell               │
├─────────────────────────────────────────────────┤
│                                                 │
│ This script will download and install the      │
│ following:                                      │
│   - Chocolatey                                  │
│   - Python 3                                    │
│   - Visual Studio Build Tools                  │
│                                                 │
│ Type ENTER to continue or Ctrl+C to cancel:    │
│ _                                               │
└─────────────────────────────────────────────────┘
```

### Actions:
1. **Press ENTER**
2. **Wait 5-10 minutes** (it downloads and installs tools)
3. You'll see lots of text scrolling
4. **Don't close the window!**
5. When finished, you'll see:
   ```
   Installation complete!
   Press any key to continue . . .
   ```
6. **Press any key**
7. Window closes automatically

---

## ✅ **STEP 4: Verify Installation**

### What to Do:
1. **CLOSE** your current PowerShell/Terminal window
2. **Open a NEW** PowerShell/Terminal:
   - Press `Win + X`
   - Click "Windows PowerShell" or "Terminal"

### Test Commands:

```powershell
node --version
```

**What You Should See:**
```
v20.11.0
```
✅ If you see a version number, Node.js is installed!

```powershell
npm --version
```

**What You Should See:**
```
10.2.4
```
✅ If you see a version number, npm is installed!

---

## 🚀 **STEP 5: Install Your Chatbot**

Now you're ready! Run these commands:

### 1. Navigate to Project
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship
```

### 2. Install Dependencies
```powershell
npm install
```

**What You'll See:**
```
npm WARN deprecated ...
npm WARN deprecated ...

added 1247 packages, and audited 1248 packages in 2m

127 packages are looking for funding
  run `npm fund` for details

found 0 vulnerabilities
```

**Timeline:**
- Takes 2-5 minutes
- Downloads ~300 MB
- Creates `node_modules` folder

### 3. Start the Application
```powershell
npm start
```

**What You'll See:**
```
⠙ Building...

Initial Chunk Files   | Names         |  Raw Size
main.js               | main          |   2.50 MB
polyfills.js          | polyfills     |  90.00 kB
styles.css            | styles        |  10.00 kB

✔ Compiled successfully.

** Angular Live Development Server is listening on localhost:4200,
   open your browser on http://localhost:4200/ **
```

### 4. Open Browser

**Automatically:** Browser might open

**Manually:** 
1. Open Chrome/Firefox/Edge
2. Go to: `http://localhost:4200`

---

## 🎉 **SUCCESS! What You'll See:**

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  SIDEBAR          │        MAIN AREA               │
│  (Gray)           │        (White)                 │
│                   │                                │
│  [+ New chat]     │         🤖                     │
│                   │                                │
│                   │  How can I help you today?     │
│  Conversations:   │                                │
│  (empty)          │  ┌─────────┐  ┌─────────┐     │
│                   │  │ 💻      │  │ 🎧      │     │
│                   │  │ Best    │  │ Noise   │     │
│  [🌙] Dark mode   │  │ laptop  │  │ cancel  │     │
│  [🗑️] Clear all   │  └─────────┘  └─────────┘     │
│                   │                                │
│                   │  ┌─────────┐  ┌─────────┐     │
│                   │  │ 📚      │  │ 🎮      │     │
│                   │  │ Learn   │  │ Gaming  │     │
│                   │  │ web dev │  │ setup   │     │
│                   │  └─────────┘  └─────────┘     │
│                   │                                │
│                   │  ┌──────────────────────┐     │
│                   │  │ Message AI...     [➤]│     │
│                   │  └──────────────────────┘     │
└────────────────────────────────────────────────────┘
```

### Try It:
1. Click "💻 Best laptop for programming"
2. See beautiful formatted response
3. Click moon icon for dark mode
4. Start chatting!

---

## ⚠️ **Troubleshooting**

### Problem: "node is not recognized"
**Solution:**
1. Make sure you opened a NEW terminal after installing
2. Try restarting your computer
3. Reinstall Node.js

### Problem: PowerShell window closes immediately
**Solution:**
- This is normal after additional tools install
- Just open a new PowerShell window

### Problem: npm install takes forever
**Solution:**
- Be patient, first install takes 2-5 minutes
- Check your internet connection
- Make sure you have ~500 MB free space

### Problem: npm install fails
**Solution:**
```powershell
npm cache clean --force
npm install --legacy-peer-deps
```

---

## 📞 **Need Help?**

Check these files:
- `INSTALLATION_GUIDE.md` - Detailed text guide
- `QUICK_REFERENCE.md` - Command cheat sheet
- `README.md` - Full documentation

---

## ✅ **Checklist**

- [ ] Downloaded Node.js installer
- [ ] Ran installer and checked all boxes
- [ ] Additional tools installed (5-10 min wait)
- [ ] Opened NEW terminal
- [ ] `node --version` shows version number
- [ ] `npm --version` shows version number
- [ ] `npm install` completed successfully
- [ ] `npm start` running without errors
- [ ] Browser shows chatbot at localhost:4200

---

**You're almost there! Just follow each screen carefully! 🚀**


