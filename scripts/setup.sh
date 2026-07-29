#!/bin/bash
# GCP Setup Script for Incident Triage System
# Run this script once to set up required GCP resources

set -e

PROJECT_ID="${GOOGLE_CLOUD_PROJECT}"
REGION="us-central1"

echo "=== Setting up GCP Resources for Incident Triage System ==="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    --project="${PROJECT_ID}"

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create incident-triage-repo \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}" || echo "Repository may already exist"

# Create Secret Manager secrets
echo "Creating Secret Manager secrets..."
for secret in MS_GRAPH_CLIENT_ID MS_GRAPH_CLIENT_SECRET TINES_API_KEY LANGSMITH_API_KEY; do
    gcloud secrets create "${secret}" \
        --replication-policy=automatic \
        --project="${PROJECT_ID}" || echo "Secret ${secret} may already exist"
done

echo ""
echo "=== GCP Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Set secret values:"
for secret in MS_GRAPH_CLIENT_ID MS_GRAPH_CLIENT_SECRET TINES_API_KEY LANGSMITH_API_KEY; do
    echo "   echo -n 'your-value' | gcloud secrets versions add ${secret} --data-file=-"
done
echo ""
echo "2. Grant Cloud Build service account access to Secret Manager:"
echo "   SA_EMAIL=\$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')@cloudbuild.gserviceaccount.com"
echo "   gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:\${SA_EMAIL} --role=roles/secretmanager.secretAccessor"
echo ""
echo "3. The Cloud Build trigger will automatically build and deploy on push to main"
