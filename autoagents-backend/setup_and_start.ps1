#!/usr/bin/env pwsh
# AutoAgents Backend Setup and Start Script

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  AutoAgents Backend - Setup & Start" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Step 1: Check if .env file exists
Write-Host "[1/5] Checking .env configuration..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
    
    # Check for API key
    $envContent = Get-Content .env -Raw
    if ($envContent -match "CLAUDE_API_KEY=sk-ant-" -or $envContent -match "ANTHROPIC_API_KEY=sk-ant-") {
        Write-Host "  ✓ Claude API key configured" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Claude API key not found in .env!" -ForegroundColor Red
        Write-Host "  Please add your API key to the .env file" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✗ .env file not found!" -ForegroundColor Red
    Write-Host "`nCreating .env file template..." -ForegroundColor Yellow
    
    @"
# ================================================
# Claude API Configuration (REQUIRED)
# ================================================
CLAUDE_API_KEY=your-api-key-here
ANTHROPIC_API_KEY=your-api-key-here

# Claude Model
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# ================================================
# MongoDB Configuration
# ================================================
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=autoagents

# ================================================
# FastAPI Server Configuration
# ================================================
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:4200
"@ | Out-File -FilePath .env -Encoding UTF8
    
    Write-Host "  ✓ .env file created with your API key" -ForegroundColor Green
}

# Step 2: Check Python virtual environment
Write-Host "`n[2/5] Checking Python environment..." -ForegroundColor Yellow
if (Test-Path "env\Scripts\Activate.ps1") {
    Write-Host "  ✓ Virtual environment found (env)" -ForegroundColor Green
    $venvPath = "env\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "  ✓ Virtual environment found (venv)" -ForegroundColor Green
    $venvPath = "venv\Scripts\Activate.ps1"
} else {
    Write-Host "  ✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Creating virtual environment..." -ForegroundColor Yellow
    python -m venv env
    $venvPath = "env\Scripts\Activate.ps1"
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
}

# Step 3: Activate virtual environment
Write-Host "`n[3/5] Activating virtual environment..." -ForegroundColor Yellow
& $venvPath
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Step 4: Install dependencies
Write-Host "`n[4/5] Checking dependencies..." -ForegroundColor Yellow
if (Test-Path requirements.txt) {
    Write-Host "  Installing/updating requirements..." -ForegroundColor Yellow
    pip install -q -r requirements.txt
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Step 5: Start the server
Write-Host "`n[5/5] Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  Backend Server Starting" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "================================================`n" -ForegroundColor Green

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

