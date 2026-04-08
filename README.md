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

## ✅ Deployment Notes
1. Ensure `GOOGLE_APPLICATION_CREDENTIALS` is set for Firestore access locally, or use the Cloud Run default service account.
2. Enable Firestore persistence by setting:
   - `USE_FIRESTORE=true`
3. Deploy to Cloud Run using `main.app` as the service entrypoint.

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
- [ ] Cloud Run URL is live and publicly accessible
- [ ] Firestore persistence is enabled and tested
- [ ] Demo video is under 3 minutes
- [ ] Final PPT includes architecture diagram and agent workflow
- [ ] README is clear and judge-friendly

## 📄 Notes
This project is designed for rapid hackathon submission. If you want to support multi-step workflow automation, the next step is to add a workflow orchestration module that chains calendar and task actions in a single user turn.
