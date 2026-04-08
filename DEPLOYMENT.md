# Cloud Run Deployment Guide

This document explains how to deploy the Multi-Agent Productivity Assistant to Google Cloud Run and how to safely manage environment configuration.

## 1. Prepare your Cloud Run environment

1. Install and authenticate the Google Cloud SDK:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable run.googleapis.com firestore.googleapis.com
   ```

3. If you want Firestore persistence, create or enable a Firestore database in your project.

## 2. Secure configuration and secrets

- `.env` is ignored in `.gitignore` and should never be committed.
- Keep secrets and service account keys out of source control.
- Use `.env.example` as a template for required variables.

### Recommended Cloud Run secret handling

- Use Google Cloud Secret Manager for sensitive values.
- Avoid storing actual keys in repository files.
- Configure runtime environment variables in Cloud Run or Secret Manager.

Example deployment with secret environment variables:
```bash
gcloud run deploy genai-productivity-assistant \
  --image=gcr.io/YOUR_PROJECT_ID/genai-productivity-assistant:latest \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars=USE_FIRESTORE=true,PORT=8080
```

For secrets managed by Secret Manager:
```bash
gcloud run services update genai-productivity-assistant \
  --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=projects/YOUR_PROJECT_ID/secrets/YOUR_SECRET_NAME:latest
```

## 3. Firestore and service account setup

- Cloud Run normally uses the attached service account to access Firestore.
- For local development only, provide `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON file.
- In production, grant the Cloud Run service account the following roles:
  - `roles/datastore.user`
  - `roles/datastore.viewer`
  - `roles/cloudrun.invoker` (if needed for other services)

## 4. Build and push the container

1. Build the Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/genai-productivity-assistant
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy genai-productivity-assistant \
     --image=gcr.io/YOUR_PROJECT_ID/genai-productivity-assistant \
     --region=us-central1 \
     --platform=managed \
     --allow-unauthenticated \
     --set-env-vars=USE_FIRESTORE=true,PORT=8080
   ```

## 5. Local development

1. Copy `.env.example` to `.env` and fill required values.
2. For Firestore testing locally, set:
   ```bash
   USE_FIRESTORE=true
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ```
3. Run the app locally:
   ```bash
   python main.py
   ```

## 6. Notes for submission

- Ensure `.env` stays private and is not committed.
- Confirm `README.md` and `DEPLOYMENT.md` provide the required setup details.
- Use Cloud Run environment variables and Secret Manager instead of hard-coding credentials.
