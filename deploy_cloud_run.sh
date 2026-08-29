#!/usr/bin/env bash
# deploy_cloud_run.sh - Deploy NaMo Engine to Google Cloud Run & setup Cloud Scheduler jobs

set -e

PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "arctic-signer-471822-i8")
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    PROJECT_ID="arctic-signer-471822-i8"
fi

REGION="asia-southeast1" # Bangkok/Singapore region
SERVICE_NAME="namo-sovereign-engine"

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: GCP Project ID is not set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi

echo "🚀 Deploying ${SERVICE_NAME} to Cloud Run in ${REGION} (Project: ${PROJECT_ID})..."

# Build and Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
    --source . \
    --region ${REGION} \
    --allow-unauthenticated \
    --platform managed \
    --port 8080 \
    --min-instances 0 \
    --max-instances 2 \
    --memory 1Gi \
    --cpu 1

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "✅ Cloud Run Service Deployed at: ${SERVICE_URL}"

# Setup Cloud Scheduler Job 1: Midnight Memory Consolidation (0 0 * * * = Midnight)
echo "📅 Creating Cloud Scheduler Job: midnight-dream-loop..."
gcloud scheduler jobs create http midnight-dream-loop \
    --schedule="0 0 * * *" \
    --uri="${SERVICE_URL}/v1/system/consolidate-memory" \
    --http-method=POST \
    --time-zone="Asia/Bangkok" \
    --location=${REGION} \
    --attempt-deadline=180s \
    || gcloud scheduler jobs update http midnight-dream-loop \
        --schedule="0 0 * * *" \
        --uri="${SERVICE_URL}/v1/system/consolidate-memory" \
        --time-zone="Asia/Bangkok" \
        --location=${REGION}

# Setup Cloud Scheduler Job 2: 12-Hour Idle Ping (0 */12 * * *)
echo "📅 Creating Cloud Scheduler Job: idle-ping-12h..."
gcloud scheduler jobs create http idle-ping-12h \
    --schedule="0 */12 * * *" \
    --uri="${SERVICE_URL}/v1/system/consolidate-memory" \
    --http-method=POST \
    --time-zone="Asia/Bangkok" \
    --location=${REGION} \
    --attempt-deadline=60s \
    || gcloud scheduler jobs update http idle-ping-12h \
        --schedule="0 */12 * * *" \
        --uri="${SERVICE_URL}/v1/system/consolidate-memory" \
        --time-zone="Asia/Bangkok" \
        --location=${REGION}

echo "🎉 Deployment & Cloud Scheduler Setup Complete!"
