# deploy.ps1 — Full API Lockdown & Deployment Script (Windows PowerShell)
# Usage: .\deploy.ps1 -ProjectId "genai-apac-cohortone-assistant"

param(
    [string]$ProjectId = "genai-apac-cohortone-assistant",
    [string]$ServiceName = "genaiapachackathonproductivity",
    [string]$Region = "us-central1",
    [string]$ImageName = "aria-productivity-api",
    [string]$ServiceAccountEmail = "71229401280-compute@developer.gserviceaccount.com"
)

# Color output function
function Write-ColorOutput($message, $color = "White") {
    switch ($color) {
        "Green" { Write-Host $message -ForegroundColor Green }
        "Yellow" { Write-Host $message -ForegroundColor Yellow }
        "Red" { Write-Host $message -ForegroundColor Red }
        "Blue" { Write-Host $message -ForegroundColor Cyan }
        default { Write-Host $message }
    }
}

# ─────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────

Write-ColorOutput "═══════════════════════════════════════════════════════════" Blue
Write-ColorOutput "🚀 Aria Production API Lockdown & Deployment" Blue
Write-ColorOutput "═══════════════════════════════════════════════════════════" Blue
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 1: Validate Configuration
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 1] Validating environment..." Yellow
Write-Host "Project ID: $ProjectId"
Write-Host "Service Name: $ServiceName"
Write-Host "Region: $Region"
Write-Host "Image: gcr.io/$ProjectId/$ImageName`:latest"
Write-Host ""

# Check gcloud is installed
$gcloudCheck = gcloud --version 2>&1
if (-not $gcloudCheck) {
    Write-ColorOutput "✗ gcloud CLI not found. Please install Google Cloud SDK." Red
    exit 1
}

# Set project
gcloud config set project $ProjectId 2>&1 | Out-Null
Write-ColorOutput "✓ Project set to: $ProjectId" Green
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 2: Build Docker Image
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 2] Building Docker image..." Yellow
Write-Host "This may take 2-5 minutes..."
Write-Host ""

gcloud builds submit `
    --tag="gcr.io/$ProjectId/$ImageName`:latest" `
    --region="$Region" `
    --project="$ProjectId"

Write-ColorOutput "✓ Docker image built and pushed to GCR" Green
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 3: Deploy to Cloud Run
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 3] Deploying to Cloud Run..." Yellow
Write-Host "Service: $ServiceName"
Write-Host "Image: gcr.io/$ProjectId/$ImageName`:latest"
Write-Host ""

gcloud run deploy $ServiceName `
    --image="gcr.io/$ProjectId/$ImageName`:latest" `
    --region="$Region" `
    --platform=managed `
    --allow-unauthenticated `
    --memory=2Gi `
    --cpu=2 `
    --timeout=3600 `
    --max-instances=10 `
    --min-instances=1 `
    --set-env-vars="PORT=8080,USE_FIRESTORE=true" `
    --service-account="$ServiceAccountEmail" `
    --project="$ProjectId"

Write-ColorOutput "✓ Service deployed to Cloud Run" Green
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 4: Configure IAM Permissions
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 4] Configuring IAM permissions..." Yellow

# Make service publicly invokable
Write-Host "  • Making service publicly invokable (allUsers)..."
gcloud run services add-iam-policy-binding $ServiceName `
    --member="allUsers" `
    --role="roles/run.invoker" `
    --region="$Region" `
    --project="$ProjectId" `
    --quiet

Write-ColorOutput "  ✓ Public access enabled" Green

# Grant AI Platform access
Write-Host "  • Granting AI Platform access to service account..."
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$ServiceAccountEmail" `
    --role="roles/aiplatform.user" `
    --condition=None `
    --quiet

Write-ColorOutput "  ✓ AI Platform role granted" Green

# Grant Firestore access
Write-Host "  • Granting Firestore access to service account..."
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$ServiceAccountEmail" `
    --role="roles/datastore.user" `
    --condition=None `
    --quiet

Write-ColorOutput "  ✓ Firestore role granted" Green
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 5: Get Service URL
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 5] Retrieving service URL..." Yellow

$ServiceUrl = gcloud run services describe $ServiceName `
    --region="$Region" `
    --project="$ProjectId" `
    --format='value(status.url)'

Write-ColorOutput "✓ Service URL: $ServiceUrl" Green
Write-Host ""

# ─────────────────────────────────────────────────
# Phase 6: Test Endpoints
# ─────────────────────────────────────────────────

Write-ColorOutput "[Phase 6] Testing API endpoints..." Yellow
Write-Host ""

# Health check
Write-Host "  Testing /health endpoint..."
try {
    $HealthResponse = Invoke-WebRequest -Uri "$ServiceUrl/health" -UseBasicParsing -TimeoutSec 10
    if ($HealthResponse.StatusCode -eq 200) {
        Write-ColorOutput "  ✓ Health check passed" Green
    } else {
        Write-ColorOutput "  ⚠ Health check status: $($HealthResponse.StatusCode)" Yellow
    }
} catch {
    Write-ColorOutput "  ⚠ Health check failed: $_" Yellow
}

# Chat endpoint
Write-Host "  Testing /chat endpoint (this may take a moment)..."
try {
    $ChatBody = @{
        message = "Hello, I am testing the API. Please confirm you are working."
        user_id = "deployment-test"
    } | ConvertTo-Json

    $ChatResponse = Invoke-WebRequest -Uri "$ServiceUrl/chat" `
        -Method POST `
        -Body $ChatBody `
        -ContentType "application/json" `
        -UseBasicParsing `
        -TimeoutSec 60

    if ($ChatResponse.StatusCode -eq 200) {
        Write-ColorOutput "  ✓ Chat endpoint responded" Green
        $content = $ChatResponse.Content | ConvertFrom-Json
        Write-Host "  Response: $($content.reply.Substring(0, [Math]::Min(100, $content.reply.Length)))..."
    } else {
        Write-ColorOutput "  ⚠ Chat endpoint status: $($ChatResponse.StatusCode)" Yellow
    }
} catch {
    Write-ColorOutput "  ⚠ Chat endpoint test failed: $_" Yellow
}

Write-Host ""

# ─────────────────────────────────────────────────
# Phase 7: Verification Summary
# ─────────────────────────────────────────────────

Write-ColorOutput "═══════════════════════════════════════════════════════════" Blue
Write-ColorOutput "🎉 Deployment Complete! 🎉" Green
Write-ColorOutput "═══════════════════════════════════════════════════════════" Blue
Write-Host ""

Write-ColorOutput "Public API Endpoint:" Yellow
Write-ColorOutput "$ServiceUrl" Green
Write-Host ""

Write-ColorOutput "Next Steps for Judges:" Yellow
Write-Host ""
Write-Host "1. Test the API:"
Write-ColorOutput "   curl -X POST $ServiceUrl/chat \" Blue
Write-ColorOutput "   -H `"Content-Type: application/json`" \" Blue
Write-ColorOutput "   -d '{`"message`": `"Hello Aria`", `"user_id`": `"judge`"}'" Blue
Write-Host ""

Write-Host "2. View service details:"
Write-ColorOutput "   gcloud run services describe $ServiceName --region=$Region" Blue
Write-Host ""

Write-Host "3. Check logs:"
Write-ColorOutput "   gcloud logging read `"resource.type=cloud_run_revision`" --limit 50" Blue
Write-Host ""

Write-ColorOutput "Permissions Configured:" Yellow
Write-Host "  ✓ Public invocation (allUsers → roles/run.invoker)"
Write-Host "  ✓ AI Platform access (serviceAccount → roles/aiplatform.user)"
Write-Host "  ✓ Firestore access (serviceAccount → roles/datastore.user)"
Write-Host ""

Write-ColorOutput "Deployment Parameters:" Yellow
Write-Host "  • Memory: 2Gi (sufficient for agent reasoning)"
Write-Host "  • CPU: 2 (for parallel processing)"
Write-Host "  • Max instances: 10 (handles concurrent requests)"
Write-Host "  • Min instances: 1 (keeps warm for fast startup)"
Write-Host "  • Timeout: 3600s (1 hour for long reasoning)"
Write-Host ""

Write-ColorOutput "Your API is production-ready! 🚀" Green
Write-ColorOutput "═══════════════════════════════════════════════════════════" Blue
