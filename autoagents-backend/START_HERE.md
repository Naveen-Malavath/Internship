# 🚀 Quick Start Guide

## Current Status

✅ **Backend Setup**: Complete  
✅ **MongoDB**: Connected & Working  
✅ **Environment File**: Created  
❌ **API Credits**: Need to add credits

---

## ⚠️ ACTION REQUIRED: Add API Credits

Your API key needs credits before you can start the application.

### Step 1: Add Credits
1. Visit: https://console.anthropic.com/settings/billing
2. Sign in with your Anthropic account
3. Add at least **$10 in credits** (recommended for testing)
4. Credits are usually available immediately

### Step 2: Verify Your .env File

Open the `.env` file (already open in Notepad) and ensure it has:

```bash
CLAUDE_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here
```

**Make sure both lines have the same API key!**

### Step 3: Save and Close Notepad

Save the `.env` file and close Notepad.

---

## 🎯 Start Your Backend (After Adding Credits)

### Option A: Automated Setup (Recommended)
```powershell
cd autoagents-backend
.\setup_and_start.ps1
```

### Option B: Quick Start
```powershell
cd autoagents-backend
.\quick_start.ps1
```

### Option C: Manual Start
```powershell
cd autoagents-backend
.\env\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## ✅ Verify Everything Works

After starting, test your setup:

```powershell
# In a NEW terminal window:
cd autoagents-backend
python test_connections.py
```

You should see:
```
✅ Anthropic API: PASS
✅ MongoDB: PASS
```

---

## 🌐 Access Your Application

Once the backend is running:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:4200 (start separately)

---

## 📊 What Each Component Does

| Component | Status | Purpose |
|-----------|--------|---------|
| **Claude API** | ❌ Needs Credits | AI-powered feature generation, stories, diagrams |
| **MongoDB Atlas** | ✅ Working | Data storage (projects, features, stories) |
| **FastAPI Backend** | ⏳ Ready to Start | REST API server |
| **Virtual Environment** | ✅ Configured | Python dependencies isolated |

---

## 🆘 Troubleshooting

### Problem: "Credit balance too low"
**Solution**: Add credits at https://console.anthropic.com/settings/billing

### Problem: "Module not found"
**Solution**: 
```powershell
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problem: "Port 8000 already in use"
**Solution**: Kill existing process or use different port:
```powershell
python -m uvicorn app.main:app --reload --port 8001
```

### Problem: MongoDB connection failed
**Solution**: Your MongoDB is already working! No action needed.

---

## 💰 Pricing Estimate

- Feature generation: ~$0.01-0.02 per request
- Story generation: ~$0.01-0.02 per request
- Diagram generation: ~$0.02-0.05 per request
- **Total for testing (50 requests)**: ~$1-2

**Recommended starting credits: $10-20**

---

## 📝 Next Steps

1. ✅ Add credits to your Anthropic account
2. ✅ Verify `.env` file has correct API key
3. ✅ Save and close Notepad
4. 🚀 Run `.\setup_and_start.ps1`
5. 🧪 Test with `python test_connections.py`
6. 🎉 Start building!

---

## 📚 Additional Resources

- **Setup Guide**: `SETUP_CLAUDE_API.md`
- **Environment Config**: `ENV_CONFIGURATION.md`
- **MongoDB Setup**: `MONGODB_SETUP.md`
- **Chatbot Guide**: `CHATBOT_QUICK_START.md`

---

**Questions? Check the logs when running the backend for detailed error messages.**

