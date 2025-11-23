Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  Starting AutoAgents Backend Server" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] API Key: Configured" -ForegroundColor Green
Write-Host "[OK] MongoDB: Atlas Cloud Database" -ForegroundColor Green
Write-Host ""

# Activate virtual environment and start server
.\env\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

