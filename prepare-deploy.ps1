# Deployment Preparation Script

Write-Host "🚀 Preparing Honeypot for Deployment..." -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git already initialized" -ForegroundColor Green
}

# Create .gitignore if it doesn't exist
if (-not (Test-Path ".gitignore")) {
    Write-Host "⚠️  .gitignore not found! Creating one..." -ForegroundColor Yellow
    @"
__pycache__/
*.pyc
.env
venv/
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
}

# Add all files
Write-Host "📝 Adding files to git..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "💾 Creating commit..." -ForegroundColor Yellow
git commit -m "Initial commit: Agentic Honey-Pot Scam Intelligence Dashboard"

Write-Host ""
Write-Host "✅ Repository prepared!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Create a new repository on GitHub" -ForegroundColor White
Write-Host "2. Copy the repository URL (e.g., https://github.com/notishwar/honeypot-scam-ai.git)" -ForegroundColor White
Write-Host "3. Run these commands:" -ForegroundColor White
Write-Host ""
Write-Host "   git remote add origin YOUR_GITHUB_URL" -ForegroundColor Yellow
Write-Host "   git branch -M main" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Then follow DEPLOYMENT.md for hosting options!" -ForegroundColor White
Write-Host ""
Write-Host "🎉 Happy Deploying!" -ForegroundColor Cyan
