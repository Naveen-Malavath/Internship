#!/usr/bin/env pwsh
# Quick Start Script - Minimal version

Write-Host "`n🚀 Starting AutoAgents Backend...`n" -ForegroundColor Cyan

# Activate virtual environment
if (Test-Path "env\Scripts\Activate.ps1") {
    & .\env\Scripts\Activate.ps1
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

