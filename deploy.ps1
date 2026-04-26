# Veritas Deployment Script (PowerShell)
# Deploys Veritas to GCP Cloud Run + Firebase Hosting

# Colors and formatting
function Write-Status {
    param([string]$Message, [string]$Status)
    $colors = @{
        'ok' = 'Green'
        'warn' = 'Yellow'
        'error' = 'Red'
        'info' = 'Cyan'
    }
    Write-Host $Message -ForegroundColor $colors[$Status]
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
    Write-Host "â•‘  $($Title.PadRight(38))  â•‘" -ForegroundColor Cyan
    Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
    Write-Host ""
}

# Start
Write-Header "Veritas Deployment (Windows)"

# Step 1: Check Prerequisites
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Yellow
Write-Host ""

$tools = @{
    'gcloud' = 'Google Cloud SDK'
    'node' = 'Node.js'
    'npm' = 'npm'
    'python' = 'Python 3'
}

foreach ($tool in $tools.GetEnumerator()) {
    try {
        $version = & $tool.Key --version 2>$null
        Write-Status "âœ“ $($tool.Value) found" -Status 'ok'
    } catch {
        Write-Status "âœ— $($tool.Value) not found" -Status 'error'
        Write-Host "Install from: https://cloud.google.com/sdk/docs/install"
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Configuration" -ForegroundColor Yellow
Write-Host ""

$projectId = Read-Host "Enter your GCP Project ID"
if ([string]::IsNullOrEmpty($projectId)) {
    Write-Status "Project ID cannot be empty" -Status 'error'
    exit 1
}

$geminiKey = Read-Host "Enter your Gemini API Key (it will be hidden)"
if ([string]::IsNullOrEmpty($geminiKey)) {
    Write-Status "Gemini API Key cannot be empty" -Status 'error'
    exit 1
}

$region = Read-Host "Enter your GCP region (default: us-central1)"
if ([string]::IsNullOrEmpty($region)) { $region = "us-central1" }

Write-Status "Configuration:" -Status 'ok'
Write-Host "  Project ID: $projectId"
Write-Host "  Region: $region"
Write-Host "  Gemini Key: [HIDDEN]"
Write-Host ""

# Step 3: Set up GCP project
Write-Host "Step 3: Setting up GCP project..." -ForegroundColor Yellow
Write-Host ""

gcloud config set project $projectId 2>$null
Write-Status "âœ“ Project set to $projectId" -Status 'ok'

Write-Host "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com 2>$null
gcloud services enable run.googleapis.com 2>$null
gcloud services enable containerregistry.googleapis.com 2>$null
Write-Status "âœ“ APIs enabled" -Status 'ok'

# Step 4: Build and deploy backend
Write-Host ""
Write-Host "Step 4: Building and deploying backend..." -ForegroundColor Yellow
Write-Host ""

Push-Location backend

Write-Host "Building Docker image..."
$buildOutput = gcloud builds submit --tag gcr.io/$projectId/veritas-backend 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Status "Backend build failed" -Status 'error'
    Write-Host $buildOutput
    exit 1
}
Write-Status "âœ“ Backend image built" -Status 'ok'

Write-Host ""
Write-Host "Deploying to Cloud Run..."
$deployOutput = gcloud run deploy veritas-backend `
  --image gcr.io/$projectId/veritas-backend `
  --platform managed `
  --region $region `
  --allow-unauthenticated `
  --memory 512Mi `
  --cpu 1 `
  --timeout 300 `
  --set-env-vars GEMINI_API_KEY=$geminiKey `
  --format='value(status.url)' 2>&1

$backendUrl = $deployOutput | Select-Object -Last 1
if ([string]::IsNullOrEmpty($backendUrl)) {
    Write-Status "Backend deployment failed" -Status 'error'
    Write-Host $deployOutput
    exit 1
}

Write-Status "âœ“ Backend deployed" -Status 'ok'
Write-Host "Backend URL: $backendUrl" -ForegroundColor Blue

# Step 5: Test backend
Write-Host ""
Write-Host "Step 5: Testing backend..." -ForegroundColor Yellow
Write-Host ""

Start-Sleep -Seconds 5
try {
    $healthCheck = Invoke-WebRequest -Uri "$backendUrl/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($healthCheck.StatusCode -eq 200) {
        Write-Status "âœ“ Backend health check passed" -Status 'ok'
    }
} catch {
    Write-Status "âš  Could not verify backend yet (may still be starting)" -Status 'warn'
}

# Step 6: Set up frontend
Write-Host ""
Write-Host "Step 6: Setting up frontend..." -ForegroundColor Yellow
Write-Host ""

Pop-Location
Push-Location frontend

"VITE_API_URL=$backendUrl" | Out-File -FilePath ".env.local" -Encoding UTF8
Write-Status "âœ“ Frontend .env.local configured" -Status 'ok'

Write-Host "Installing frontend dependencies..."
npm install --legacy-peer-deps --silent 2>$null
Write-Status "âœ“ Dependencies installed" -Status 'ok'

Write-Host ""
Write-Host "Building frontend..."
npm run build 2>&1 | Select-Object -Last 5

if (-not (Test-Path "dist")) {
    Write-Status "Frontend build failed" -Status 'error'
    exit 1
}
Write-Status "âœ“ Frontend built" -Status 'ok'

$buildSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "Build size: $([Math]::Round($buildSize, 2)) MB"

# Step 7: Set up Firebase
Write-Host ""
Write-Host "Step 7: Setting up Firebase..." -ForegroundColor Yellow
Write-Host ""

try {
    firebase --version >$null 2>&1
} catch {
    Write-Host "Installing Firebase CLI..."
    npm install -g firebase-tools --silent
}
Write-Status "âœ“ Firebase CLI ready" -Status 'ok'

Write-Host ""
Write-Host "Initializing Firebase project..."
firebase init hosting --project=$projectId --quiet 2>$null
Write-Status "âœ“ Firebase initialized" -Status 'ok'

# Step 8: Deploy frontend
Write-Host ""
Write-Host "Step 8: Deploying frontend..." -ForegroundColor Yellow
Write-Host ""

$deployOutput = firebase deploy --only hosting --project=$projectId 2>&1
$firebaseUrl = $deployOutput | Select-String -Pattern 'https://.*web\.app' | Select-Object -First 1 -ExpandProperty Line
if ([string]::IsNullOrEmpty($firebaseUrl)) {
    $firebaseUrl = "https://$projectId.web.app"
}

Write-Status "âœ“ Frontend deployed" -Status 'ok'
Write-Host "Frontend URL: $firebaseUrl" -ForegroundColor Blue

# Step 9: Update CORS
Write-Host ""
Write-Host "Step 9: Updating CORS for production..." -ForegroundColor Yellow
Write-Host ""

Pop-Location
Push-Location backend

Write-Host "Updating backend/main.py with production CORS..."

$mainContent = Get-Content "main.py"
$mainContent = $mainContent -replace 'allow_origins=\[.*?\]', @"
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "$firebaseUrl",
]
"@

$mainContent | Out-File -FilePath "main.py" -Encoding UTF8 -Force
Write-Status "âœ“ CORS updated" -Status 'ok'

Write-Host ""
Write-Host "Redeploying backend with updated CORS..."
gcloud run deploy veritas-backend `
  --image gcr.io/$projectId/veritas-backend `
  --region $region `
  2>$null

Write-Status "âœ“ Backend redeployed" -Status 'ok'

Pop-Location

# Final summary
Write-Host ""
Write-Host "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—" -ForegroundColor Cyan
Write-Host "â•‘  Veritas Deployment (Windows)          â•‘" -ForegroundColor Cyan
Write-Host "â•‘  Bias Auditing Tool for ML Models      â•‘" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•" -ForegroundColor Cyan
Write-Host ""

Write-Status "ðŸŽ‰ Veritas is now live!" -Status 'ok'
Write-Host ""
Write-Host "URLs:" -ForegroundColor Blue
Write-Host "  Backend: $backendUrl"
Write-Host "  Frontend: $firebaseUrl"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit: $firebaseUrl"
Write-Host "2. Select 'Hiring' domain"
Write-Host "3. Click 'Use Sample Data'"
Write-Host "4. Should see results in 2-3 seconds"
Write-Host ""
Write-Host "Monitoring:" -ForegroundColor Yellow
Write-Host "  Backend logs: gcloud run logs read veritas-backend --limit 50 --project=$projectId"
Write-Host "  Firebase logs: firebase open hosting --project=$projectId"
Write-Host ""
Write-Host "Support:" -ForegroundColor Yellow
Write-Host "  Deployment guide: ./DEPLOYMENT_FREE_TIER.md"
Write-Host "  Troubleshooting: ./DEPLOYMENT_FREE_TIER.md"
Write-Host ""

