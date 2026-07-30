# Tines Intelligent Workflow Design Skill

## Overview
This skill provides enterprise-grade guidance for designing Tines workflows following the seven principles of intelligent workflow design, enhanced with patterns from the Tines Library.

## Files

| File | Purpose | Status |
|------|---------|--------|
| [SKILL.md](SKILL.md) | The rulebook: seven principles, decision framework, library patterns | ✅ |
| [TEMPLATE.md](TEMPLATE.md) | Workflow design template for new Tines Stories | ✅ |
| [INCIDENT_TRIAGE_STORY.md](INCIDENT_TRIAGE_STORY.md) | Incident triage story outline with patterns | ✅ |
| [M365_INCIDENT_TRIAGE_BLUEPRINT.md](M365_INCIDENT_TRIAGE_BLUEPRINT.md) | Strategic blueprint with rationale | ✅ |
| [TINES_STORY_SPEC.md](TINES_STORY_SPEC.md) | Ready-to-build Tines story specification | ✅ |
| [VALIDATION_AND_PREVIEW.md](VALIDATION_AND_PREVIEW.md) | Validation results + dry-run preview | ✅ |
| [FACTORY_WORKFLOW.md](FACTORY_WORKFLOW.md) | Multi-agent factory documentation | ✅ |

## Quick Start

1. **Define the outcome** before building (Principle 1)
2. **Classify each step** as deterministic, agentic, or human-in-the-loop (Principle 2)
3. **Design exception paths** - assume systems will fail (Principle 3)
4. **Build governance in** - don't bolt it on (Principle 4)
5. **Make HITL explicit** - it's a design choice, not a fallback (Principle 5)
6. **Stay vendor-agnostic** - API-first integrations (Principle 6)
7. **Layer your architecture** - triggers, logic, actions, orchestration (Principle 7)

## Document Flow

```
TEMPLATE.md → Blueprint → Story Spec → Validation → Preview → Approval → Tines API
```

| Stage | Document | Agent |
|-------|----------|-------|
| Design | `M365_INCIDENT_TRIAGE_BLUEPRINT.md` | Architect |
| Spec | `TINES_STORY_SPEC.md` | Builder |
| Validation | `VALIDATION_AND_PREVIEW.md` | Tester + Documenter |
| Creation | Tines API | Creator (after approval) |

## M365 Incident Triage Status

| Component | Status |
|-----------|--------|
| Blueprint | ✅ Complete |
| Specification | ✅ Complete |
| Validation | ✅ Passed (95%) |
| Dry-Run Preview | ✅ Complete |
| Tines Story Creation | ⏳ **BLOCKED** - Awaiting credentials |

### Required for Story Creation

```bash
export TINES_API_KEY="your-tines-api-key"
export TINES_TENANT_URL="https://your-tenant.tines.com"
export FOLDER_ID="your-folder-id"
```

## Sources

- [Seven principles of intelligent workflow design](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [Tines Library - Incidents and Alerts](https://www.tines.com/library/use-cases/incidents-and-alerts/)
- [Tines Library - Security](https://www.tines.com/library/teams/security/)
- [Tines API Documentation](https://docs.tines.com/en/)
