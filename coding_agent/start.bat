@echo off
echo ============================================================
echo Starting AI Coding Agent Web UI
echo ============================================================
echo.

echo Starting backend server...
start /B cmd /C "env\Scripts\python.exe -m uvicorn src.web.server:app --reload --port 8000"

timeout /t 3 >nul

echo Starting frontend server...
cd frontend
start /B cmd /C "npm run dev"
cd..

echo.
echo ============================================================
echo Servers are starting!
echo ============================================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo.
echo Press any key to open the UI in your browser...
pause >nul

start http://localhost:5173

echo.
echo Press Ctrl+C to stop the servers
pause
