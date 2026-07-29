#!/bin/bash
# GCP Setup Script for Incident Triage System
# Run this script once to set up all required GCP resources

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
    clouddeploy.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    vpcaccess.googleapis.com \
    --project="${PROJECT_ID}"

# Create service accounts
echo "Creating service accounts..."

# Dev service account
gcloud iam service-accounts create incident-triage-dev \
    --display-name="Incident Triage Dev" \
    --project="${PROJECT_ID}"

# Staging service account
gcloud iam service-accounts create incident-triage-staging \
    --display-name="Incident Triage Staging" \
    --project="${PROJECT_ID}"

# Prod service account
gcloud iam service-accounts create incident-triage-prod \
    --display-name="Incident Triage Production" \
    --project="${PROJECT_ID}"

# Grant Cloud Run permissions to service accounts
echo "Granting Cloud Run permissions..."
for env in dev staging prod; do
    SA="incident-triage-${env}@${PROJECT_ID}.iam.gserviceaccount.com"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA}" \
        --role="roles/run.admin"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA}" \
        --role="roles/iam.serviceAccountUser"
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA}" \
        --role="roles/secretmanager.secretAccessor"
done

# Create Artifact Registry repository
echo "Creating Artifact Registry repository..."
gcloud artifacts repositories create incident-triage-repo \
    --repository-format=docker \
    --location="${REGION}" \
    --project="${PROJECT_ID}"

# Configure Docker authentication
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --project="${PROJECT_ID}"

# Create VPC Connector for private networking
echo "Creating VPC Connector..."
gcloud compute networks vpc-access connectors create incident-triage-vpc-connector \
    --region="${REGION}" \
    --subnet=incident-triage-subnet \
    --subnet-project="${PROJECT_ID}" \
    --min-instances=2 \
    --max-instances=10 \
    --project="${PROJECT_ID}" || echo "VPC connector may already exist"

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
    echo "   gcloud secrets versions add ${secret} --data-file=-"
done
echo ""
echo "2. Create Cloud Build triggers:"
echo "   gcloud builds triggers import --source=cloudbuild/trigger.yaml"
echo ""
echo "3. Create Cloud Deploy pipeline:"
echo "   gcloud deploy apply --file=clouddeploy/delivery-pipeline.yaml --region=${REGION}"
echo ""
echo "4. Deploy the application:"
echo "   gcloud builds run cloudbuild/cloudbuild.yaml --substitutions=_REGION=${REGION}"
