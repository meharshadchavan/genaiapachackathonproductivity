# 📋 Quick API Reference for Judges

**Aria — Multi-Agent Productivity Assistant**  
**GenAI APAC Hackathon 2026**

---

## 🚀 Live API Endpoint

```
https://genaiapachackathonproductivity-xxxxx.run.app
```

*Replace `xxxxx` with the actual service ID shown in deployment output*

---

## 📡 Endpoints Overview

| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| `/` | GET | Land on interactive UI | None |
| `/health` | GET | API health status | None |
| `/profile` | GET | Retrieve user preferences | None |
| `/chat` | POST | **Main endpoint** - Send message to Aria | None |
| `/tasks` | GET | List all tasks | None |
| `/tasks` | POST | Create new task | None |
| `/events` | GET | List all events | None |
| `/events` | POST | Create new event | None |

---

## 🎯 The Main Endpoint: `/chat`

### Request Format

```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Your instruction here",
    "user_id": "optional_user_id"
  }'
```

### Request Body (JSON)

```json
{
  "message": "string (required) - What you want Aria to do",
  "user_id": "string (optional) - Identifies the user session, defaults to 'default'"
}
```

### Response Format

```json
{
  "status": "ok",
  "reply": "Aria's response text",
  "user_id": "the_user_id_used"
}
```

---

## ✅ Example Interactions

### Example 1: Create a Task
**Request:**
```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a high-priority task to review the demo by Friday",
    "user_id": "judge-001"
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "reply": "I've created a high-priority task 'Review the demo' with a due date of Friday. It's saved to your task list.",
  "user_id": "judge-001"
}
```

---

### Example 2: Schedule a Meeting
**Request:**
```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Schedule a project kickoff meeting tomorrow at 3 PM with the team",
    "user_id": "judge-001"
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "reply": "I've scheduled a 'Project Kickoff' meeting for tomorrow at 3:00 PM. Attendees have been noted as 'the team'.",
  "user_id": "judge-001"
}
```

---

### Example 3: Update User Profile
**Request:**
```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Judge and my timezone is Asia/Singapore",
    "user_id": "judge-001"
  }'
```

**Expected Response:**
```json
{
  "status": "ok",
  "reply": "Got it! I've saved your profile: Name = Judge, Timezone = Asia/Singapore. I'll use this to personalize your experience.",
  "user_id": "judge-001"
}
```

---

### Example 4: Multi-Turn Conversation
**Message 1:**
```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My name is Judge",
    "user_id": "judge-001"
  }'
```

**Message 2 (same session):**
```bash
curl -X POST https://genaiapachackathonproductivity-xxxxx.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my name?",
    "user_id": "judge-001"
  }'
```

**Response:**
```json
{
  "status": "ok",
  "reply": "Your name is Judge. I'm remembering that in your profile!",
  "user_id": "judge-001"
}
```

---

## 🔍 Testing via Browser UI

Simply visit:
```
https://genaiapachackathonproductivity-xxxxx.run.app
```

You'll see an interactive dashboard where you can:
- 💬 Chat with Aria in a text interface
- 📋 View and manage tasks
- 📅 Schedule events
- 👤 Update your profile

---

## 🛠️ Health Check

Verify the API is running:

```bash
curl -X GET https://genaiapachackathonproductivity-xxxxx.run.app/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "message": "API is running",
  "agents": 4
}
```

---

## 📊 What "4 Agents" Means

1. **Manager Agent (Aria)** - Primary coordinator that understands intent
2. **Task Agent** - Handles to-do creation, completion, deletion
3. **Calendar Agent** - Manages meetings, events, scheduling
4. **Personalization Agent** - Stores user preferences, name, timezone

---

## 🧠 System Architecture

```
User Message 
    ↓
[Manager Agent - Aria]  ← Routes to the right specialist
    ↓
    ├─→ [Task Agent]           (for tasks)
    ├─→ [Calendar Agent]       (for events)
    ├─→ [Personalization Agent](for profile)
    └─→ [Tool Execution]       (Firestore, Google Calendar API)
    ↓
[Response] → Back to User
```

---

## 🚨 Error Handling

### 503 - Service Initializing
```json
{"detail": "Agent not initialized yet. Try again in a moment."}
```
**Solution**: Wait 10 seconds and retry. The system is warming up.

### 400 - Invalid Request
```json
{"detail": "Request validation error"}
```
**Solution**: Ensure JSON is valid and contains required fields.

### 500 - Internal Error
```json
{"detail": "Internal server error"}
```
**Solution**: Check the gcloud logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

---

## 📞 Support Commands

### View API Logs (Last 50 entries)
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=genaiapachackathonproductivity" \
  --limit 50 \
  --format=json
```

### View Service Status
```bash
gcloud run services describe genaiapachackathonproductivity --region=us-central1
```

### Check Active Revisions
```bash
gcloud run revisions list --service=genaiapachackathonproductivity --region=us-central1
```

---

## 💡 Pro Tips for Judges

1. **Start Simple**: Begin with "Create a task: Learn about Aria"
2. **Test Delegation**: Try "Schedule a meeting tomorrow and create a task to prepare"
3. **Verify Memory**: Set your name, then ask "What is my name?" to confirm session persistence
4. **Test Multi-Turn**: Use the same `user_id` in multiple requests to verify context carryover
5. **Check Firestore**: If `USE_FIRESTORE=true`, data persists across API restarts

---

## 📈 Performance Notes

- **First request**: May take 3-5 seconds (startup time)
- **Subsequent requests**: Typically 1-2 seconds
- **Timeout**: 3600 seconds (1 hour) for long reasoning tasks
- **Concurrent requests**: Up to 10 simultaneous in production

---

## ✅ Submission Checklist for Judges

- [ ] API endpoint is publicly accessible (no authentication)
- [ ] `/health` returns `200 OK`
- [ ] `/chat` accepts POST requests with proper JSON
- [ ] Multi-turn conversations maintain context (`user_id`)
- [ ] Tasks are created and persisted
- [ ] Events are scheduled correctly
- [ ] User profile is saved and recalled
- [ ] Natural language is understood (not just hardcoded queries)
- [ ] Undo functionality works (optional but impressive)
- [ ] Firestore integration is active (`USE_FIRESTORE=true`)

---

**Last Updated**: April 8, 2026  
**Status**: Production Ready ✅
