# Environment Configuration Guide

## ⚠️ CRITICAL: API Key Credit Issue

Your current API key has insufficient credits. You need to:

### Option 1: Add Credits to Your Account
1. Visit: https://console.anthropic.com/settings/billing
2. Add credits (minimum $5-10 recommended)
3. Your existing API key will work once credits are added

### Option 2: Use New API Key
If you have a different API key with credits, update both lines in `.env`:

```bash
CLAUDE_API_KEY=your-new-api-key-here
ANTHROPIC_API_KEY=your-new-api-key-here
```

## Complete .env File Template

Copy this into your `.env` file (replace with your actual API key):

```bash
# ================================================
# Claude API Configuration (REQUIRED)
# ================================================
CLAUDE_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here

# Claude Model (Optional - uses default if not specified)
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# ================================================
# MongoDB Configuration (Already Working!)
# ================================================
MONGODB_URL=mongodb+srv://uppinaik0920_db_user:YOUR_PASSWORD@cluster0.lfspdlo.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=autoagents_db

# ================================================
# FastAPI Server Configuration
# ================================================
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:4200

# ================================================
# Development Settings (Optional)
# ================================================
# CLAUDE_MODEL_DEBUG=claude-3-haiku-20240307  # Cheaper model for testing
```

## API Key from Your Message

The API key you mentioned in your message:
```
your-api-key-here
```

**Update BOTH lines in .env:**
- Line with `CLAUDE_API_KEY=`
- Line with `ANTHROPIC_API_KEY=`

## Current Status

✅ **MongoDB**: Working perfectly - Connected to Atlas Cloud
❌ **Anthropic API**: Insufficient credits

## After Adding Credits

Once you've added credits or updated the API key:

### Windows PowerShell:
```powershell
cd autoagents-backend
.\setup_and_start.ps1
```

### Or Quick Start:
```powershell
cd autoagents-backend
.\quick_start.ps1
```

### Or Manual Start:
```powershell
cd autoagents-backend
.\env\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing After Setup

Run this to verify everything works:
```powershell
python test_connections.py
```

You should see:
```
✅ Anthropic API: PASS
✅ MongoDB: PASS
```

## Pricing Information

- Each AI request costs approximately $0.01-0.05 USD
- Minimum recommended credit: $10 for testing
- Check pricing: https://www.anthropic.com/pricing

## Need Help?

1. **Check API credits**: https://console.anthropic.com/settings/billing
2. **Get API keys**: https://console.anthropic.com/settings/keys
3. **View usage**: https://console.anthropic.com/settings/usage

