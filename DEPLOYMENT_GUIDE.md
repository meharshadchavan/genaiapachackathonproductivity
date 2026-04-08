# 🚀 Production Deployment Guide - Aria Multi-Agent Productivity Assistant

**Repository**: https://github.com/meharshadchavan/genaiapachackathonproductivity  
**Last Updated**: April 8, 2026  
**Status**: ✅ Production-Ready

---

## 📋 Pre-Deployment Validation

All core components have been validated:

✅ **ADK Integration**: Multi-agent system with Manager Agent (Aria) and 3 sub-agents
✅ **Code Quality**: All imports resolved, no runtime errors
✅ **API Endpoints**: 7 REST endpoints fully functional
✅ **Database**: Firestore integration confirmed
✅ **GitHub**: Repository updated with latest commits

---

## 🔧 Quick Local Test (Before Deployment)

```bash
# Navigate to project
cd c:\Users\Harshad\Documents\PROJECTS\genaiapachackathonproductivity

# Validate environment
python -c "from agent import root_agent; from main import app; print('✅ Ready')"

# Kill any existing process on port 8080 (Windows)
netsh int ipv4 show tcpstats
Taskkill /PID <PID> /F

# Start the server
python main.py

# In another terminal, test the chat endpoint
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show my tasks", "user_id": "test"}'
```

---

## ☁️ Cloud Run Deployment

### Option 1: Using gcloud CLI (Recommended)

```bash
# Set project
gcloud config set project YOUR_GCP_PROJECT_ID

# Authenticate
gcloud auth login

# Deploy to Cloud Run
gcloud run deploy aria-productivity-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 3600 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=YOUR_GCP_PROJECT_ID"
```

### Option 2: Using Docker (For local testing)

```bash
# Build Docker image
docker build -t aria-productivity:latest .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  aria-productivity:latest

# Push to Google Container Registry
docker tag aria-productivity:latest gcr.io/YOUR_PROJECT_ID/aria-productivity:latest
docker push gcr.io/YOUR_PROJECT_ID/aria-productivity:latest

# Deploy from GCR
gcloud run deploy aria-productivity-assistant \
  --image gcr.io/YOUR_PROJECT_ID/aria-productivity:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi
```

### Option 3: GitHub Actions Auto-Deploy

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      - run: gcloud run deploy aria-productivity-assistant \
          --source . \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

---

## 🔑 Environment Variables

Required for deployment:

```env
# Firebase/Firestore
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Gemini API (Optional - ADK handles this)
GOOGLE_API_KEY=your-api-key

# API Configuration
ENVIRONMENT=production
API_PORT=8080
```

---

## 📊 API Endpoints (Post-Deployment)

Once deployed, use these endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/chat` | Send message to Aria |
| GET | `/health` | Health check |
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks |
| POST | `/events` | Create calendar event |
| GET | `/events` | List events |
| GET | `/profile` | Get user profile |

**Example Request**:
```bash
curl -X POST https://aria-productivity-assistant-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add task: Submit hackathon project by Friday",
    "user_id": "harshad"
  }'
```

---

## ✅ Post-Deployment Validation

After deployment, run these checks:

```bash
# 1. Health check
curl https://your-service-url/health

# 2. Chat endpoint
curl -X POST https://your-service-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'

# 3. View Cloud Run logs
gcloud run logs read aria-productivity-assistant --limit 50

# 4. Monitor metrics
gcloud monitoring dashboards create --config=file://dashboard.yaml
```

---

## 🛑 Rollback Plan

If deployment fails:

```bash
# Revert to previous version
git revert HEAD
git push origin main

# Or rollback Cloud Run revision
gcloud run services update-traffic aria-productivity-assistant \
  --to-revisions PREVIOUS_REVISION=100
```

---

## 📝 Maintenance Checklist

- [ ] Monitor Cloud Run logs for errors
- [ ] Check Firestore database quota usage
- [ ] Test all endpoints weekly
- [ ] Review and update dependencies monthly
- [ ] Monitor API latency (target: <1s)
- [ ] Backup Firestore data regularly

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8080 in use | `lsof -i :8080` (Linux/Mac) or `netstat -ano \| findstr :8080` (Windows) |
| Firestore auth fails | Check `GOOGLE_APPLICATION_CREDENTIALS` path and permissions |
| ADK import errors | Ensure `google-adk` is installed: `pip install google-adk` |
| High latency | Scale up Cloud Run memory or check Firestore indices |

---

## 📞 Support & Resources

- **ADK Documentation**: https://cloud.google.com/agent-infrastructure/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Firestore Docs**: https://firebase.google.com/docs/firestore
- **GitHub Issues**: https://github.com/meharshadchavan/genaiapachackathonproductivity/issues

---

**Ready to deploy!** 🎉
