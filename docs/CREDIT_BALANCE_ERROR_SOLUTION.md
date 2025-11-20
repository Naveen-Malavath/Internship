# Solving Credit Balance Error

## Problem

You're seeing this error:
```
[agent1] CREDIT BALANCE ERROR: Anthropic API credit balance is too low. 
Please add credits to your Anthropic account at https://console.anthropic.com/settings/billing 
to continue using Agent-1.
```

## Solution: Add Credits to Your Anthropic Account

### Step 1: Go to Anthropic Console
1. Visit: https://console.anthropic.com/settings/billing
2. Sign in to your Anthropic account

### Step 2: Add Credits
1. Click on "Add Credits" or "Purchase Credits"
2. Select the amount you want to add
3. Complete the payment process

### Step 3: Verify Credits
1. Check your credit balance in the billing dashboard
2. Wait a few moments for the credits to be applied
3. Try your request again

## Alternative: Development Mode with Mock Responses

If you're in development and don't want to use API credits, you can enable a mock mode that returns sample responses.

### Enable Mock Mode

**Option 1: Environment Variable**
```bash
export AGENT_MOCK_MODE=true
```

**Option 2: Add to `.env` file**
```bash
# In autoagents-backend/.env
AGENT_MOCK_MODE=true
```

**Option 3: Set when starting server**
```bash
AGENT_MOCK_MODE=true python -m uvicorn app.main:app --reload
```

### What Mock Mode Does

- Returns 8 domain-specific mock features based on your prompt
- No API calls are made (saves credits)
- Features are customized based on keywords in your prompt:
  - E-commerce prompts → shopping cart, checkout, inventory features
  - Healthcare prompts → patient management, appointments, records
  - Banking prompts → accounts, transactions, payments
  - Education prompts → courses, assignments, grading
  - Default → generic application features

### Example Mock Output

For a healthcare prompt, you'll get:
- Patient Registration and Management
- Appointment Scheduling System
- Medical Records Management
- Prescription Management
- Billing and Insurance Processing
- Doctor Dashboard
- Lab Results Integration
- Telemedicine Capabilities

### Disable Mock Mode

Remove the environment variable or set it to false:
```bash
unset AGENT_MOCK_MODE
# or
export AGENT_MOCK_MODE=false
```

## Frontend Error Handling

The frontend should display the error message to users. The error response includes:
- **Status Code**: `402 Payment Required`
- **Error Message**: User-friendly message with billing link

Make sure your frontend handles 402 status codes and displays the error message to users.

## Testing After Adding Credits

1. Restart your backend server
2. Try generating features again
3. Check logs to confirm API calls are successful

## Prevention

- Monitor your credit balance regularly
- Set up billing alerts in Anthropic console
- Consider using mock mode for development/testing

