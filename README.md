# LangGraph Incident Triage System

A multi-agent incident triage system built with LangGraph for automated incident response. Deploys to Google Cloud Run with CI/CD via Cloud Build and Cloud Deploy.

## Architecture

The system consists of 5 specialized agents:

1. **Research Agent** - Collects context from Microsoft Graph and external sources
2. **Architect Agent** - Analyzes patterns and determines resolution strategy
3. **Builder Agent** - Generates remediation scripts
4. **Tester Agent** - Validates remediation scripts
5. **Documenter Agent** - Creates incident reports

## Quick Start

### Prerequisites

- Python 3.11+
- Docker
- Google Cloud SDK
- GCP Project with billing enabled

### Local Development

```bash
# Clone and install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run locally
python main.py
```

### API Endpoints

- `GET /health` - Health check (for load balancer probes)
- `GET /ready` - Readiness check
- `POST /triage` - Process single incident
- `POST /triage/batch` - Process multiple incidents
- `GET /` - API information

### Example Request

```bash
curl -X POST http://localhost:8080/triage \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-001",
    "incident_data": {
      "type": "network",
      "priority": "high",
      "affectedServices": ["api-gateway", "auth-service"]
    }
  }'
```

## Deployment

### One-Time GCP Setup

```bash
# Set your project
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Set secret values (replace with actual values)
echo "your-client-id" | gcloud secrets versions add MS_GRAPH_CLIENT_ID --data-file=-
echo "your-client-secret" | gcloud secrets versions add MS_GRAPH_CLIENT_SECRET --data-file=-
echo "your-tines-key" | gcloud secrets versions add TINES_API_KEY --data-file=-
echo "your-langsmith-key" | gcloud secrets versions add LANGSMITH_API_KEY --data-file=-
```

### Manual Deployment

```bash
# Deploy to dev
./scripts/deploy.sh dev

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh prod
```

### CI/CD Pipeline

The project uses Cloud Build for CI/CD:

1. **Push to main** → Builds Docker image → Deploys to dev & staging
2. **Pull requests** → Quick validation (lint, test, build)
3. **Manual approval** → Deploys to production

To create triggers:

```bash
gcloud builds triggers import --source=cloudbuild/trigger.yaml
```

### Cloud Deploy Pipeline

For managed deployments with approval gates:

```bash
# Create targets
gcloud deploy apply --file=clouddeploy/target-dev.yaml --region=us-central1
gcloud deploy apply --file=clouddeploy/target-staging.yaml --region=us-central1
gcloud deploy apply --file=clouddeploy/target-prod.yaml --region=us-central1

# Create pipeline
gcloud deploy apply --file=clouddeploy/delivery-pipeline.yaml --region=us-central1

# Rollout to dev
gcloud deploy rollouts create manual-001 \
    --delivery-pipeline=incident-triage-pipeline \
    --region=us-central1 \
    --annotations="commit-sha=$(git rev-parse HEAD)"
```

## Scaling Configuration

| Environment | Min Instances | Max Instances | Memory | CPU |
|-------------|---------------|---------------|--------|-----|
| Dev         | 0             | 2             | 512Mi  | 1   |
| Staging     | 0             | 5             | 1Gi    | 2   |
| Production  | 1             | 10            | 2Gi    | 2   |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MS_GRAPH_CLIENT_ID` | Azure AD application client ID | Yes |
| `MS_GRAPH_CLIENT_SECRET` | Azure AD application client secret | Yes |
| `TINES_API_KEY` | Tines API key for workflow integration | Yes |
| `LANGSMITH_API_KEY` | LangSmith API key for tracing | Yes |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI models) | No |
| `ENVIRONMENT` | Deployment environment | Auto |

## Project Structure

```
.
├── agents/               # Multi-agent system
│   ├── __init__.py
│   ├── base.py          # Base agent class
│   ├── research.py      # Research agent
│   ├── architect.py     # Architect agent
│   ├── builder.py       # Builder agent
│   ├── tester.py        # Tester agent
│   └── documenter.py    # Documenter agent
├── cloudbuild/          # Cloud Build configurations
│   ├── cloudbuild.yaml
│   ├── cloudbuild-pr.yaml
│   └── trigger.yaml
├── clouddeploy/         # Cloud Deploy configurations
│   ├── delivery-pipeline.yaml
│   ├── target-dev.yaml
│   ├── target-staging.yaml
│   ├── target-prod.yaml
│   └── skaffold.yaml
├── scripts/             # Deployment scripts
│   ├── setup.sh
│   └── deploy.sh
├── main.py              # FastAPI app + LangGraph orchestrator
├── requirements.txt
├── langgraph.json
├── Dockerfile
└── README.md
```

## Security

- Runs as non-root user in container
- Secrets stored in Secret Manager
- Service accounts with minimal permissions
- VPC Connector for private networking
- Production requires manual approval

## Free Tier Usage

This deployment is designed to use GCP free tier where possible:

- Cloud Run: 2 million requests/month free
- Cloud Build: 120 build-minutes/day free
- Artifact Registry: 0.5 GB storage free
- Secret Manager: 6 active secrets free
- Cloud Deploy: Free for up to 5 targets

## License

MIT
