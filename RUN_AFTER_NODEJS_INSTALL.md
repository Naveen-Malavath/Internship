# 🚀 Run These Commands After Installing Node.js

After you've installed Node.js and opened a NEW terminal, run these commands:

## Step 1: Navigate to Project
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship
```

## Step 2: Verify Node.js Installation
```powershell
node --version
```
**Expected output:** `v20.11.0` (or similar)

```powershell
npm --version
```
**Expected output:** `10.2.4` (or similar)

## Step 3: Install Dependencies (takes 2-5 minutes)
```powershell
npm install
```
**Expected output:**
```
added 1247 packages, and audited 1248 packages in 2m
found 0 vulnerabilities
```

## Step 4: Start the Application
```powershell
npm start
```
**Expected output:**
```
✔ Compiled successfully.
** Angular Live Development Server is listening on localhost:4200 **
```

## Step 5: Open Browser
Open your browser and go to:
```
http://localhost:4200
```

---

## 🎉 What You'll See

### Welcome Screen:
- Robot emoji 🤖
- "How can I help you today?"
- 4 colorful suggestion cards
- Sidebar on the left
- Input box at bottom

### Try This:
1. Click "💻 Best laptop for programming"
2. See the bot respond with MacBook Pro details
3. Click the moon icon 🌙 to try dark mode

---

## ⚠️ If You Get Errors

### "npm is not recognized"
→ Node.js not installed properly
→ Make sure you opened a NEW terminal after installation
→ Try restarting your computer

### "Port 4200 already in use"
→ Run: `npm start -- --port 4300`
→ Open: http://localhost:4300

### Module errors during npm install
→ Try: `npm install --legacy-peer-deps`

---

## 📞 Quick Help

- **Installation taking too long?** Be patient, first install takes 2-5 minutes
- **Blank screen in browser?** Press F12 to check for errors
- **Server won't start?** Check terminal for red error messages

**Good luck! Your ChatGPT-style chatbot will be running soon! 🚀**


