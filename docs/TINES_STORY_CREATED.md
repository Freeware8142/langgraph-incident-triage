# Tines Story - m365-incident-triage

## Created Story Details

| Field | Value |
|-------|-------|
| **Story Name** | m365-incident-triage |
| **Story ID** | 595 |
| **GUID** | 9dc8f6b4feb3341cd371caeb474ea756 |
| **Slug** | m365_incident_triage |
| **Tenant** | hidden-mountain-5366.tines.com |
| **Team ID** | 209 (Your first team) |
| **Mode** | LIVE |
| **Created** | 2026-07-30T01:14:00Z |

## Story URL

```
https://hidden-mountain-5366.tines.com/stories/m365_incident_triage
```

## Story Description

Production incident triage workflow for Microsoft 365 security events. Receives alerts from Defender/Sentinel, enriches via Microsoft Graph API, classifies severity with AI, and routes to appropriate response path with human approval gates for high-risk actions. Business outcome: Reduce MTTR by 60%.

## Next Steps

### 1. Add Credentials to the Story

The story requires the following credentials. Add them through the Tines UI:

1. Go to **Credentials** in the story
2. Add each credential:

| Credential Name | Type | Description |
|----------------|------|-------------|
| `microsoft_graph_client_id` | Text | Azure AD application client ID |
| `microsoft_graph_client_secret` | Text | Azure AD application client secret |
| `microsoft_graph_tenant_id` | Text | Azure AD tenant ID |
| `slack_webhook_url` | Text | Slack webhook URL for notifications |
| `jira_api_token` | Text | Jira API token |

### 2. Build the Story Actions

The story is created but empty. Use the specification file to build the actions:

- **Specification:** `.agents/skills/tines-workflow-design/TINES_STORY_SPEC.md`
- **Actions to add:** ~30 actions across 4 layers

### 3. Configure Webhook Trigger

Add a webhook trigger to receive alerts from Microsoft Defender or Sentinel.

### 4. Test the Workflow

1. Send a test webhook payload
2. Verify enrichment calls Microsoft Graph
3. Test approval gate escalation

## Specification Reference

For the complete action list and configuration:

- [TINES_STORY_SPEC.md](../.agents/skills/tines-workflow-design/TINES_STORY_SPEC.md) - Full specification
- [M365_INCIDENT_TRIAGE_BLUEPRINT.md](../.agents/skills/tines-workflow-design/M365_INCIDENT_TRIAGE_BLUEPRINT.md) - Design rationale

## API Access

The story can be managed via Tines API:

```bash
# Get story details
curl -H "Authorization: Bearer $TINES_API_KEY" \
  "https://hidden-mountain-5366.tines.com/api/v1/stories/595"

# Update story
curl -X PATCH -H "Authorization: Bearer $TINES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "updated-name"}' \
  "https://hidden-mountain-5366.tines.com/api/v1/stories/595"
```

## Workflow Summary

| Component | Count |
|-----------|-------|
| Total Actions | ~30 |
| Layers | 4 |
| Approval Gates | 4 |
| Reusable Sub-Stories | 4 |

### Mode Classification

| Mode | Count | Examples |
|------|-------|----------|
| Deterministic | 18 | Ingestion, enrichment, orchestration |
| Agentic | 4 | AI classification steps |
| Human-in-the-Loop | 3 | Approval gates, verification |

### Approval Gates

| Gate | Trigger | Timeout |
|------|---------|---------|
| Analyst Review | High severity | 30 min |
| Manager Approval | Critical severity | 15 min |
| CISO Approval | Manager escalation | 30 min |
| User Verification | Destructive action | 15 min |
