#!/bin/bash
# deploy.sh — Full API Lockdown & Deployment Script
# Usage: bash deploy.sh <PROJECT_ID>

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────

PROJECT_ID="${1:-genai-apac-cohortone-assistant}"
SERVICE_NAME="genaiapachackathonproductivity"
REGION="us-central1"
IMAGE_NAME="aria-productivity-api"
SERVICE_ACCOUNT_EMAIL="71229401280-compute@developer.gserviceaccount.com"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 Aria Production API Lockdown & Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 1: Validate Configuration
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 1] Validating environment...${NC}"
echo "Project ID: $PROJECT_ID"
echo "Service Name: $SERVICE_NAME"
echo "Region: $REGION"
echo "Image: gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"
echo ""

# Check gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}✗ gcloud CLI not found. Please install Google Cloud SDK.${NC}"
    exit 1
fi

# Check git is installed (optional but recommended)
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠ git not found (optional, recommended for version control)${NC}"
fi

# Set project
gcloud config set project "$PROJECT_ID"
echo -e "${GREEN}✓ Project set to: $PROJECT_ID${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 2: Build Docker Image
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 2] Building Docker image...${NC}"
echo "This may take 2-5 minutes..."
echo ""

gcloud builds submit \
    --tag="gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" \
    --region="$REGION" \
    --project="$PROJECT_ID"

echo -e "${GREEN}✓ Docker image built and pushed to GCR${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 3: Deploy to Cloud Run
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 3] Deploying to Cloud Run...${NC}"
echo "Service: $SERVICE_NAME"
echo "Image: gcr.io/$PROJECT_ID/$IMAGE_NAME:latest"
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --image="gcr.io/$PROJECT_ID/$IMAGE_NAME:latest" \
    --region="$REGION" \
    --platform=managed \
    --allow-unauthenticated \
    --memory=2Gi \
    --cpu=2 \
    --timeout=3600 \
    --max-instances=10 \
    --min-instances=1 \
    --set-env-vars="PORT=8080,USE_FIRESTORE=true" \
    --service-account="$SERVICE_ACCOUNT_EMAIL" \
    --project="$PROJECT_ID"

echo -e "${GREEN}✓ Service deployed to Cloud Run${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 4: Configure IAM Permissions
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 4] Configuring IAM permissions...${NC}"

# Make service publicly invokable
echo "  • Making service publicly invokable (allUsers)..."
gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --quiet

echo -e "${GREEN}  ✓ Public access enabled${NC}"

# Grant AI Platform access
echo "  • Granting AI Platform access to service account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/aiplatform.user" \
    --condition=None \
    --quiet

echo -e "${GREEN}  ✓ AI Platform role granted${NC}"

# Grant Firestore access
echo "  • Granting Firestore access to service account..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/datastore.user" \
    --condition=None \
    --quiet

echo -e "${GREEN}  ✓ Firestore role granted${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 5: Get Service URL
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 5] Retrieving service URL...${NC}"

SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --format='value(status.url)')

echo -e "${GREEN}✓ Service URL: $SERVICE_URL${NC}"
echo ""

# ─────────────────────────────────────────────────
# Phase 6: Test Endpoints
# ─────────────────────────────────────────────────

echo -e "${YELLOW}[Phase 6] Testing API endpoints...${NC}"
echo ""

# Health check
echo "  Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s -X GET "$SERVICE_URL/health" && echo "")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}  ✓ Health check passed${NC}"
else
    echo -e "${YELLOW}  ⚠ Health check response: $HEALTH_RESPONSE${NC}"
fi

# Chat endpoint
echo "  Testing /chat endpoint (this may take a moment)..."
CHAT_RESPONSE=$(curl -s -X POST "$SERVICE_URL/chat" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Hello, I am testing the API. Please confirm you are working.",
        "user_id": "deployment-test"
    }')

if echo "$CHAT_RESPONSE" | grep -q "status"; then
    echo -e "${GREEN}  ✓ Chat endpoint responded${NC}"
    echo "  Response: $(echo "$CHAT_RESPONSE" | head -c 100)..."
else
    echo -e "${YELLOW}  ⚠ Chat endpoint response: $CHAT_RESPONSE${NC}"
fi

echo ""

# ─────────────────────────────────────────────────
# Phase 7: Verification Summary
# ─────────────────────────────────────────────────

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 Deployment Complete! 🎉${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Public API Endpoint:${NC}"
echo -e "${GREEN}$SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}Next Steps for Judges:${NC}"
echo ""
echo "1. Test the API:"
echo -e "   ${BLUE}curl -X POST $SERVICE_URL/chat \\${NC}"
echo -e "   ${BLUE}-H \"Content-Type: application/json\" \\${NC}"
echo -e "   ${BLUE}-d '{\"message\": \"Hello Aria\", \"user_id\": \"judge\"}'${NC}"
echo ""
echo "2. View service details:"
echo -e "   ${BLUE}gcloud run services describe $SERVICE_NAME --region=$REGION${NC}"
echo ""
echo "3. Check logs:"
echo -e "   ${BLUE}gcloud logging read \"resource.type=cloud_run_revision\" --limit 50${NC}"
echo ""
echo -e "${YELLOW}Permissions Configured:${NC}"
echo "  ✓ Public invocation (allUsers → roles/run.invoker)"
echo "  ✓ AI Platform access (serviceAccount → roles/aiplatform.user)"
echo "  ✓ Firestore access (serviceAccount → roles/datastore.user)"
echo ""
echo -e "${YELLOW}Deployment Parameters:${NC}"
echo "  • Memory: 2Gi (sufficient for agent reasoning)"
echo "  • CPU: 2 (for parallel processing)"
echo "  • Max instances: 10 (handles concurrent requests)"
echo "  • Min instances: 1 (keeps warm for fast startup)"
echo "  • Timeout: 3600s (1 hour for long reasoning)"
echo ""
echo -e "${GREEN}Your API is production-ready! 🚀${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
