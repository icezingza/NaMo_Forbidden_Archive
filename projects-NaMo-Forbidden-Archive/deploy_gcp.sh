#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- Configuration variables (Change these to match your GCP project) ---
PROJECT_ID="your-gcp-project-id"        # GCP Project ID
SERVICE_NAME="namo-forbidden-archive"   # Cloud Run Service Name
REGION="asia-east1"                     # Region (Taiwan is excellent for Thailand latency)
BUCKET_NAME="namo-session-storage"      # Google Cloud Storage bucket name for persistent memory

echo "====================================================="
echo " Starting Deploy Procedure: NaMo Forbidden Archive"
echo "====================================================="

# Step 1: Set Google Cloud Project
echo "1. Setting GCP project to: $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

# Step 2: Create Google Cloud Storage bucket for persistent sessions if it doesn't exist
echo "2. Checking GCS Bucket for persistent sessions..."
if ! gcloud storage buckets describe "gs://$BUCKET_NAME" &>/dev/null; then
    echo "Creating GCS Bucket gs://$BUCKET_NAME in $REGION..."
    gcloud storage buckets create "gs://$BUCKET_NAME" --location="$REGION"
else
    echo "GCS Bucket gs://$BUCKET_NAME already exists."
fi

# Step 3: Build Docker Image using Google Cloud Build
echo "3. Building Docker image using Cloud Build..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Step 4: Deploy to Google Cloud Run
echo "4. Deploying service to Google Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --set-env-vars "USE_GCS=true" \
    --set-env-vars "GCS_BUCKET_NAME=$BUCKET_NAME" \
    --set-env-vars "GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE" # It is safer to use GCP Secret Manager instead of plain text, but this is a starting point.

echo "====================================================="
echo " DEPLOYMENT COMPLETE!"
echo " Service URL can be retrieved using: gcloud run services describe $SERVICE_NAME --region $REGION --format='value(status.url)'"
echo "====================================================="
