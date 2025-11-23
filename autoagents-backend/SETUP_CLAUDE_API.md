# Claude API Setup Guide

## ⚠️ CRITICAL: Fix 503 Service Unavailable Error

The 503 errors you're seeing occur because the Claude API key is not configured. Follow these steps:

## Step 1: Get Your Claude API Key

1. Visit https://console.anthropic.com/
2. Sign up or log in to your Anthropic account
3. Navigate to "API Keys" in the dashboard
4. Create a new API key or copy an existing one
5. The key will look like: `sk-ant-api03-...`

## Step 2: Create .env File

Create a file named `.env` in the `autoagents-backend` directory with the following content:

```bash
# Claude API Configuration (REQUIRED)
CLAUDE_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE

# Claude Model
CLAUDE_MODEL=claude-sonnet-4-20250514

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=autoagents

# FastAPI Configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:4200
```

**IMPORTANT**: Replace `sk-ant-api03-YOUR-ACTUAL-KEY-HERE` with your actual Claude API key!

## Step 3: Restart Backend Server

After creating the `.env` file:

```bash
cd autoagents-backend
# Stop the backend if it's running (Ctrl+C)
# Then restart it:
.\start_backend.ps1
# OR
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Verify Setup

Once restarted, the architecture visualization dropdown should work:

1. Open frontend at http://localhost:4200
2. Create a project with features and stories
3. Click the "Diagram Type" dropdown
4. Select "HLD", "LLD", or "DBD"
5. The diagram should generate without 503 errors

## Diagram Types Explained

- **HLD (High Level Design)**: System architecture & business flow
- **LLD (Low Level Design)**: Component interactions & implementation details
- **DBD (Database Design)**: Entity-Relationship diagrams & data models

## Troubleshooting

### Still Getting 503 Errors?

1. Check that `.env` file exists in `autoagents-backend` directory
2. Verify the API key is correct (no extra spaces/quotes)
3. Check backend logs for specific error messages
4. Ensure you have API credits available in your Anthropic account

### Check Backend Logs

Look for these messages in the terminal running the backend:

✅ **Working correctly**:
```
[agent3] Initialized with Claude Sonnet 4.5 model: claude-sonnet-4-20250514
[agent3] Starting COLORED Mermaid diagram generation
```

❌ **Not working**:
```
[claude_client] API key not configured
Agent_3 is unavailable. Missing Claude API configuration.
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `CLAUDE_API_KEY` | ✅ Yes | Your Claude API key from Anthropic |
| `ANTHROPIC_API_KEY` | ✅ Yes | Alternative name for Claude API key |
| `CLAUDE_MODEL` | ❌ No | Model to use (default: claude-sonnet-4-20250514) |
| `MONGODB_URL` | ❌ No | MongoDB connection string |
| `MONGODB_DB_NAME` | ❌ No | MongoDB database name |

## Cost Information

- Each diagram generation costs approximately 0.01-0.05 USD
- Pricing depends on diagram complexity and model used
- Check https://www.anthropic.com/pricing for current rates

