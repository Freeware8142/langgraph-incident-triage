#!/bin/bash
# Deploy Incident Triage System to Cloud Run using Cloud Build
# Usage: ./deploy.sh [dev|staging|prod]

set -e

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
REGION="us-central1"
SERVICE_NAME="incident-triage"

# Set scaling based on environment
case "${ENVIRONMENT}" in
    dev)
        MIN_INSTANCES=0
        MAX_INSTANCES=10
        MEMORY="512Mi"
        ;;
    staging)
        MIN_INSTANCES=0
        MAX_INSTANCES=10
        MEMORY="1Gi"
        ;;
    prod)
        MIN_INSTANCES=1
        MAX_INSTANCES=10
        MEMORY="1Gi"
        ;;
    *)
        echo "Unknown environment: ${ENVIRONMENT}"
        echo "Usage: ./deploy.sh [dev|staging|prod]"
        exit 1
        ;;
esac

echo "=== Deploying to ${ENVIRONMENT} ==="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"

# Run Cloud Build to build and deploy
echo "Running Cloud Build..."
gcloud builds submit \
    --tag "${REGION}-docker.pkg.dev/${PROJECT_ID}/incident-triage-repo/${SERVICE_NAME}:${ENVIRONMENT}" \
    --project="${PROJECT_ID}"

# Deploy to Cloud Run (without secrets for now - add via console if needed)
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${REGION}-docker.pkg.dev/${PROJECT_ID}/incident-triage-repo/${SERVICE_NAME}:${ENVIRONMENT}" \
    --region="${REGION}" \
    --platform=managed \
    --allow-unauthenticated \
    --min-instances="${MIN_INSTANCES}" \
    --max-instances="${MAX_INSTANCES}" \
    --memory="${MEMORY}" \
    --cpu=1 \
    --concurrency=80 \
    --timeout=60s \
    --set-env-vars="ENVIRONMENT=${ENVIRONMENT}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --format="value(status.url)")

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: ${SERVICE_URL}/health"
echo "API Docs: ${SERVICE_URL}/docs"
