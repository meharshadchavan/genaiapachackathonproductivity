# Aria: Multi-Agent Productivity Assistant
Built for Gen AI APAC Hackathon 2026

Aria is a multi-agent productivity platform built with Google ADK, Gemini 2.0 Flash, and FastAPI. It orchestrates a Manager Agent plus specialized Task, Calendar, and Personalization sub-agents, with optional Firestore persistence for state.

## 🚀 Core Features
- Manager/Worker architecture: primary `Aria` manager agent delegates to Task, Calendar, and Personalization sub-agents.
- Structured state storage: Firestore-backed persistence for events, tasks, and user profile.
- Tool integration via MCP: calendar, task, and user preference tools exposed to the agent.
- Undo support for task and event actions.
- Demo-friendly REST API with live web UI landing page.

## 🧠 Architecture
- `agent.py`: Manager agent coordinating the assistant.
- `agents/`: Sub-agent definitions.
- `tools/`: MCP tool implementations for Calendar, Tasks, and Personalization.
- `storage.py`: Shared store with optional Firestore persistence.
- `main.py`: FastAPI server exposing API endpoints and the chat interface.
- `mcp_server.py`: FastMCP server exposing the same tool functions as MCP tools.

## 🛠 Tech Stack
- LLM: Vertex AI Gemini 2.0 Flash
- Framework: Google ADK + FastAPI
- Database: Google Cloud Firestore (optional, enabled by `USE_FIRESTORE=true`)
- Deployment: Google Cloud Run

## 🚀 Production Deployment

**Status**: Ready for Cloud Run (GenAI APAC Hackathon 2026)

### Quick Start (Single Command)

**On macOS/Linux:**
```bash
bash deploy.sh genai-apac-cohortone-assistant
```

**On Windows (PowerShell):**
```powershell
.\deploy.ps1 -ProjectId "genai-apac-cohortone-assistant"
```

### What This Does
- ✅ Builds Docker image and pushes to Google Container Registry
- ✅ Deploys to Cloud Run with 2Gi memory, 2 CPU, auto-scaling
- ✅ Configures IAM: Public invocation + AI Platform + Firestore permissions
- ✅ Tests endpoints and returns live API URL
- ✅ Takes ~5-10 minutes end-to-end

### Manual Deployment
See [PRODUCTION_LOCKDOWN.md](PRODUCTION_LOCKDOWN.md) for detailed step-by-step instructions and troubleshooting.

### Comprehensive Deployment Guide
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Pre-deployment validation
- Cloud Run deployment options (gcloud CLI, Docker, GitHub Actions)
- Environment variables configuration
- Post-deployment validation checklist
- Rollback procedures
- Maintenance and monitoring

### Testing the Live API
See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for:
- Example cURL commands for judges
- Endpoint documentation
- Multi-turn conversation examples
- Browser UI access

### Pre-Deployment Checklist
See [FINAL_SUBMISSION_CHECKLIST.md](FINAL_SUBMISSION_CHECKLIST.md) for:
- Local verification steps
- GCP resource checks
- Submission requirements
- Troubleshooting guide

## ✅ Local Development

1. Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set for Firestore access locally, or use the Cloud Run default service account.
2. Enable Firestore persistence by setting:
   - `USE_FIRESTORE=true`
3. Run locally using `uvicorn` (as shown below)

## 📦 Run Locally
```bash
python -m pip install -r requirements.txt
set USE_FIRESTORE=true
set GOOGLE_APPLICATION_CREDENTIALS=path/to/creds.json
uvicorn main:app --host 0.0.0.0 --port 8080
```

## 🔧 What I fixed
- Added Firestore persistence support in `storage.py`.
- Added storage persistence calls in task, calendar, and personalization tools.
- Updated UI footer from AlloyDB to Firestore.
- Added `google-cloud-firestore` dependency.

## 📌 Submission Checklist

**Before Final Submission:**
- [ ] Run `bash deploy.sh` or `deploy.ps1` successfully
- [ ] API endpoint is live: `https://genaiapachackathonproductivity-xxxxx.run.app`
- [ ] Health check passes: `curl https://.../health`
- [ ] Chat endpoint works: `curl -X POST https://.../chat -H "Content-Type: application/json" -d '{"message":"Hello","user_id":"test"}'`
- [ ] Firestore persistence is enabled and tested
- [ ] Multi-turn conversations maintain context
- [ ] All documentation updated (see [FINAL_SUBMISSION_CHECKLIST.md](FINAL_SUBMISSION_CHECKLIST.md))
- [ ] `.env` is in `.gitignore` and NOT committed
- [ ] Repository is clean (git log shows only meaningful commits)

**For Judges:**
- 📖 Start with [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md) for testing examples
- 🌐 Access interactive UI at: `https://genaiapachackathonproductivity-xxxxx.run.app`
- 📋 Full deployment docs: [PRODUCTION_LOCKDOWN.md](PRODUCTION_LOCKDOWN.md)

## 📄 Notes
This project is designed for rapid hackathon submission. If you want to support multi-step workflow automation, the next step is to add a workflow orchestration module that chains calendar and task actions in a single user turn.
