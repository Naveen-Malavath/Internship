#!/usr/bin/env pwsh
# Test connections and start backend if everything works

Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AutoAgents - Test & Start Backend           ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Test connections first
Write-Host "🔍 Testing API and Database connections...`n" -ForegroundColor Yellow

python test_connections.py

# Check if test was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   ✅ ALL TESTS PASSED - Starting Backend      ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Green
    
    # Activate virtual environment
    if (Test-Path "env\Scripts\Activate.ps1") {
        & .\env\Scripts\Activate.ps1
    } elseif (Test-Path "venv\Scripts\Activate.ps1") {
        & .\venv\Scripts\Activate.ps1
    }
    
    Write-Host "🚀 Starting FastAPI server on http://localhost:8000`n" -ForegroundColor Cyan
    Write-Host "   📖 API Docs: http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host "   🛑 Press Ctrl+C to stop`n" -ForegroundColor Gray
    
    # Start the server
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    
} else {
    Write-Host "`n╔════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║   ❌ TESTS FAILED - Cannot Start Backend      ║" -ForegroundColor Red
    Write-Host "╚════════════════════════════════════════════════╝`n" -ForegroundColor Red
    
    Write-Host "⚠️  Please fix the issues above before starting the backend.`n" -ForegroundColor Yellow
    
    Write-Host "Common solutions:" -ForegroundColor Cyan
    Write-Host "  1. Add credits to your Anthropic account:" -ForegroundColor White
    Write-Host "     → https://console.anthropic.com/settings/billing`n" -ForegroundColor Gray
    
    Write-Host "  2. Update your API key in the .env file:" -ForegroundColor White
    Write-Host "     → notepad .env`n" -ForegroundColor Gray
    
    Write-Host "  3. Check MongoDB connection (if failing):" -ForegroundColor White
    Write-Host "     → Verify MONGODB_URL in .env file`n" -ForegroundColor Gray
    
    Write-Host "After fixing, run this script again:`n" -ForegroundColor Yellow
    Write-Host "  .\test_and_start.ps1`n" -ForegroundColor Cyan
    
    exit 1
}

