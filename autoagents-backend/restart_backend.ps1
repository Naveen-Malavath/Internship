# Restart AutoAgents Backend with new API key
Write-Host "`n=== Restarting AutoAgents Backend ===" -ForegroundColor Cyan
Write-Host "Loading new API key from .env file..." -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment and start server
.\env\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

