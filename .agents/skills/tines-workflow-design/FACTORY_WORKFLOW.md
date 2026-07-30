# Tines Story Factory

## Overview

This repository contains an autonomous workflow engineering system for creating production-ready Tines stories using LangGraph multi-agent orchestration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TINES STORY FACTORY                      │
│              (LangGraph Multi-Agent System)                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   RESEARCH    │     │   ARCHITECT   │     │    BUILDER   │
│    AGENT      │────▶│    AGENT      │────▶│    AGENT      │
└───────────────┘     └───────────────┘     └───────────────┘
                                              │
                              ┌───────────────┴───────────────┐
                              ▼                             ▼
                        ┌───────────────┐             ┌───────────────┐
                        │   TESTER     │             │ DOCUMENTER   │
                        │    AGENT     │             │    AGENT      │
                        └───────────────┘             └───────────────┘
                                      │                     │
                                      └──────────┬──────────┘
                                                 ▼
                                        ┌───────────────┐
                                        │  CREATOR    │
                                        │   AGENT     │
                                        │  (Awaiting  │
                                        │  Approval)   │
                                        └───────────────┘
```

## Agent Roles

| Agent | Purpose | Inputs | Outputs |
|-------|---------|--------|---------|
| **Research Agent** | Gather context from Tines Library, docs, patterns | Skill files, patterns | Research summary |
| **Architect Agent** | Design workflow using 7 principles | Research | Blueprint (`.md`) |
| **Builder Agent** | Convert blueprint to Tines spec | Blueprint | Story spec (`.md`) |
| **Tester Agent** | Validate against checklist | Story spec | Validation report |
| **Documenter Agent** | Create preview, dry-run, docs | Validation | Preview (`.md`) |
| **Creator Agent** | Create Tines story via API | Approval + spec | Story ID |

## Workflow Design Principles

Based on [Intelligent workflow design: seven principles for enterprise teams](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/):

1. **Start with outcomes** - Define business value before tools
2. **Match execution mode** - D/A/H per step
3. **Design for exceptions** - Expect failures
4. **Build governance in** - Audit trails, approvals
5. **Make HITL explicit** - Design-time decision
6. **Vendor-agnostic** - API-first
7. **Layer architecture** - Decoupled components

## Step Mode Classification

| Mode | Symbol | When to Use |
|------|--------|-------------|
| **Deterministic** | D | Rule-based, machine-speed |
| **Agentic** | A | AI-assisted judgment |
| **Human-in-the-Loop** | H | Manual approval required |

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The rulebook: 7 principles, patterns, checklist |
| `TEMPLATE.md` | Fill-in-the-blanks template for new stories |
| `INCIDENT_TRIAGE_STORY.md` | Sample story outline |
| `M365_INCIDENT_TRIAGE_BLUEPRINT.md` | Strategic blueprint with rationale |
| `TINES_STORY_SPEC.md` | Technical specification for implementation |
| `VALIDATION_AND_PREVIEW.md` | Validation results + dry-run preview |
| `FACTORY_WORKFLOW.md` | This file - factory documentation |

## M365 Incident Triage Example

### Business Outcome
**Reduce MTTR for M365 security incidents by 60%** while ensuring appropriate human oversight.

### Workflow Summary
- **25 steps** across 4 layers
- **18 deterministic**, **4 agentic**, **3 human-led**
- **4 approval gates** with timeout escalation
- **4 reusable sub-stories**

### Current Status

```
Blueprint: ✅ Complete
Specification: ✅ Complete
Validation: ✅ Passed (95%)
Dry-Run: ✅ Complete
Creation: ⏳ BLOCKED - Awaiting credentials
```

## Prerequisites for Story Creation

1. **Tines API Key** - From Tines tenant settings
2. **Tines Tenant URL** - e.g., `https://acme.tines.com`
3. **Folder ID** - Where to create the story

## Usage

### 1. Define the Workflow (Blueprint)

Create a markdown file following the template in `TEMPLATE.md`:
- Business outcome
- Step classification
- Layer architecture
- Failure paths

### 2. Build the Specification (Builder Agent)

Convert blueprint to Tines technical spec:
- Action list with dependencies
- API endpoints
- Credential references
- Approval gate configurations

### 3. Validate (Tester Agent)

Check against workflow design principles:
- All steps classified (D/A/H)
- Approval gates present for risky actions
- Timeout escalation configured
- Audit logging defined
- Failure paths documented

### 4. Preview (Documenter Agent)

Generate dry-run representation:
- Action count summary
- API request preview
- Required credentials
- Decision point for human approval

### 5. Create (Creator Agent)

After explicit approval:
```bash
# Set credentials
export TINES_API_KEY="your-key"
export TINES_TENANT_URL="https://your-tenant.tines.com"
export FOLDER_ID="your-folder-id"

# Creator agent will call Tines API
curl -X POST "${TINES_TENANT_URL}/api/v1/stories" \
  -H "Authorization: Bearer ${TINES_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @story-spec.json
```

## Security Considerations

- **No hardcoded secrets** - All credentials use environment variables
- **Secret Manager** - Use GCP Secret Manager for production
- **Audit logging** - All AI interactions logged
- **Approval chains** - Immutable records for compliance

## Repository Structure

```
langgraph-incident-triage/
├── agents/                    # LangGraph agent definitions
│   ├── base.py
│   ├── research.py
│   ├── architect.py
│   ├── builder.py
│   ├── tester.py
│   └── documenter.py
├── main.py                    # FastAPI app with /health
├── requirements.txt
├── Dockerfile
├── cloudbuild/               # GCP CI/CD
├── clouddeploy/             # Cloud Deploy pipeline
├── scripts/                  # Deployment scripts
└── .agents/skills/
    └── tines-workflow-design/
        ├── SKILL.md
        ├── TEMPLATE.md
        ├── INCIDENT_TRIAGE_STORY.md
        ├── M365_INCIDENT_TRIAGE_BLUEPRINT.md
        ├── TINES_STORY_SPEC.md
        ├── VALIDATION_AND_PREVIEW.md
        └── FACTORY_WORKFLOW.md  # This file
```

## Future Enhancements

- [ ] LangGraph agents integrated with Cloud Run
- [ ] Automated credential detection from Secret Manager
- [ ] Tines API integration in main.py
- [ ] Story version management
- [ ] Automated testing via Tines API

## References

- [Seven principles of intelligent workflow design](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [Tines Library - Incidents and Alerts](https://www.tines.com/library/use-cases/incidents-and-alerts/)
- [Tines Library - Security](https://www.tines.com/library/teams/security/)
- [Tines API Documentation](https://docs.tines.com/en/)
