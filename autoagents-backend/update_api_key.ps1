#!/usr/bin/env pwsh
# Script to update API key in .env file

Write-Host "`n🔧 Updating API Key in .env file...`n" -ForegroundColor Cyan

$newApiKey = "your-api-key-here"

if (Test-Path .env) {
    # Read current .env content
    $content = Get-Content .env -Raw
    
    # Update both API key lines
    $content = $content -replace 'CLAUDE_API_KEY=.*', "CLAUDE_API_KEY=$newApiKey"
    $content = $content -replace 'ANTHROPIC_API_KEY=.*', "ANTHROPIC_API_KEY=$newApiKey"
    
    # Write back to .env
    $content | Set-Content .env -NoNewline
    
    Write-Host "✅ API key updated successfully!`n" -ForegroundColor Green
    
    # Show preview
    Write-Host "Updated .env file preview:" -ForegroundColor Yellow
    Get-Content .env | Select-Object -First 5
    Write-Host ""
    
} else {
    Write-Host "❌ .env file not found!`n" -ForegroundColor Red
    exit 1
}

