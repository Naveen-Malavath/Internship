# Update API Key Script
$newKey = "your-api-key-here"

Write-Host "Updating API key..." -ForegroundColor Cyan

$content = Get-Content .env -Raw
$content = $content -replace 'CLAUDE_API_KEY=sk-ant-[^\r\n]+', "CLAUDE_API_KEY=$newKey"
$content = $content -replace 'ANTHROPIC_API_KEY=sk-ant-[^\r\n]+', "ANTHROPIC_API_KEY=$newKey"
$content | Set-Content .env -NoNewline

Write-Host "Done! API key updated." -ForegroundColor Green
Get-Content .env | Select-Object -First 3

