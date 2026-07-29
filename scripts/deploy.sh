#!/bin/bash
# Deploy Incident Triage System to Cloud Run

set -e

ENVIRONMENT="${1:-dev}"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
REGION="us-central1"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/incident-triage-repo/incident-triage"

# Determine service configuration based on environment
case "${ENVIRONMENT}" in
    dev)
        SERVICE_NAME="incident-triage-dev"
        MIN_INSTANCES=0
        MAX_INSTANCES=2
        MEMORY="512Mi"
        CPU=1
        CONCURRENCY=80
        TIMEOUT="60s"
        ;;
    staging)
        SERVICE_NAME="incident-triage-staging"
        MIN_INSTANCES=0
        MAX_INSTANCES=5
        MEMORY="1Gi"
        CPU=2
        CONCURRENCY=100
        TIMEOUT="120s"
        ;;
    prod)
        SERVICE_NAME="incident-triage"
        MIN_INSTANCES=1
        MAX_INSTANCES=10
        MEMORY="2Gi"
        CPU=2
        CONCURRENCY=200
        TIMEOUT="300s"
        ;;
    *)
        echo "Unknown environment: ${ENVIRONMENT}"
        echo "Usage: ./deploy.sh [dev|staging|prod]"
        exit 1
        ;;
esac

echo "=== Deploying to ${ENVIRONMENT} ==="
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"

# Build the Docker image
echo "Building Docker image..."
docker build -t "${IMAGE}:${ENVIRONMENT}" .

# Push to Artifact Registry
echo "Pushing to Artifact Registry..."
docker push "${IMAGE}:${ENVIRONMENT}"

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image="${IMAGE}:${ENVIRONMENT}" \
    --region="${REGION}" \
    --platform=managed \
    --min-instances="${MIN_INSTANCES}" \
    --max-instances="${MAX_INSTANCES}" \
    --memory="${MEMORY}" \
    --cpu="${CPU}" \
    --concurrency="${CONCURRENCY}" \
    --timeout="${TIMEOUT}" \
    --set-env-vars="ENVIRONMENT=${ENVIRONMENT}" \
    --vpc-connector=incident-triage-vpc-connector \
    --service-account="incident-triage-${ENVIRONMENT}@${PROJECT_ID}.iam.gserviceaccount.com"

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region="${REGION}" \
    --format="value(status.url)")

echo ""
echo "=== Deployment Complete ==="
echo "Service URL: ${SERVICE_URL}"
echo "Health Check: ${SERVICE_URL}/health"
echo "API Docs: ${SERVICE_URL}/docs"
