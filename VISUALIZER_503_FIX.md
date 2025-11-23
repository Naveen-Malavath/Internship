# Fix for 503 Service Unavailable Error on /agent/visualizer

## Problem
The `/agent/visualizer` endpoint was returning 503 Service Unavailable errors when generating diagrams (HLD, LLD, DBD). This was causing the frontend to fail when switching diagram types.

## Root Cause
The Claude API was taking too long to generate complex diagrams, causing the request to timeout without proper error handling. The endpoint had no timeout mechanism and didn't provide fallback diagrams.

## Solution Implemented

### 1. Added Timeout Handling (120 seconds)
- Wrapped the `agent3_service.generate_mermaid()` call with `asyncio.wait_for()`
- Set a 120-second timeout to prevent indefinite hanging
- Added proper timeout exception handling

### 2. Fallback Diagrams
When the Claude API times out, the system now returns simple but functional fallback diagrams:

**HLD Fallback:**
- User -> Frontend -> Backend -> AI -> Database
- Professional color-coded nodes

**LLD Fallback:**
- App Root -> Components -> Services -> API
- Component hierarchy with styling

**DBD Fallback:**
- Basic ER diagram with Users, Projects, Features, Stories
- Proper relationships and primary/foreign keys

### 3. Improved Error Logging
- Added detailed logging for timeout events
- Better error messages for debugging
- Preserves original exceptions while providing user-friendly messages

## How to Apply the Fix

### Step 1: Restart the Backend
```powershell
# Navigate to backend directory
cd C:\Users\uppin\OneDrive\Desktop\internship\autoagents-backend

# Stop any running backend (if running)
# Press Ctrl+C in the terminal where it's running

# Start the backend
.\start_backend.ps1
# OR
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Test the Fix
1. Open your frontend application (http://localhost:4200)
2. Create or open a project
3. Try switching between HLD, LLD, and DBD diagram types
4. The diagrams should now load successfully within 120 seconds
5. If Claude API times out, you'll see a simple fallback diagram instead of a 503 error

### Step 3: Monitor Logs
Watch the backend console for log messages:
- `[visualizer] Agent3 timeout for {type}, using fallback diagram` - Indicates fallback was used
- `[agent3] 🎨 Starting COLORED Mermaid diagram generation` - Indicates Agent3 is working

## Files Modified
- `autoagents-backend/app/routers/visualizer.py`
  - Added `asyncio.wait_for()` with 120-second timeout
  - Added fallback diagram generation for all three diagram types
  - Improved error handling and logging

## Expected Behavior

### Before Fix:
- ❌ 503 Service Unavailable errors
- ❌ Frontend shows "HttpErrorResponse"  
- ❌ No diagrams displayed

### After Fix:
- ✅ Diagrams load within 120 seconds
- ✅ Fallback diagrams if Claude API is slow
- ✅ Proper error messages with logging
- ✅ No frontend crashes

## Additional Notes

### If You Still See 503 Errors:
1. **Check Backend is Running:**
   ```powershell
   curl http://localhost:8000/api/status/right-now
   ```
   
2. **Check API Key:**
   ```powershell
   cd autoagents-backend
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key OK:', bool(os.getenv('ANTHROPIC_API_KEY')))"
   ```

3. **Check Logs:**
   Look for error messages in the backend console output

4. **Try Fallback Mode:**
   The system should automatically use fallback diagrams if Agent3 fails

### Performance Tips:
- HLD diagrams are fastest (simple architecture)
- LLD diagrams are moderate (component details)
- DBD diagrams are slowest (database schema analysis)
- Fallback diagrams are instant (pre-defined templates)

### Future Improvements:
- Consider caching generated diagrams
- Implement progressive diagram loading
- Add diagram complexity estimation
- Pre-generate common diagram patterns

## Troubleshooting

### Backend Won't Start:
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill the process using port 8000 if needed
Stop-Process -Id <PID>
```

### Still Getting Errors:
- Ensure MongoDB is running
- Check .env file has ANTHROPIC_API_KEY
- Verify Python environment is activated
- Check requirements are installed: `pip install -r requirements.txt`

