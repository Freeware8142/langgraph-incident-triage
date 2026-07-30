# Tines Intelligent Workflow Design Skill

## Overview
This skill provides enterprise-grade guidance for designing Tines workflows following the seven principles of intelligent workflow design, enhanced with patterns from the Tines Library.

## Files

| File | Purpose |
|-------|---------|
| [SKILL.md](SKILL.md) | The rulebook: seven principles, decision framework, library patterns, production checklist |
| [TEMPLATE.md](TEMPLATE.md) | Workflow design template for new Tines Stories |
| [INCIDENT_TRIAGE_STORY.md](INCIDENT_TRIAGE_STORY.md) | Incident triage story outline with patterns |
| [M365_INCIDENT_TRIAGE_BLUEPRINT.md](M365_INCIDENT_TRIAGE_BLUEPRINT.md) | **Production-ready M365 incident triage blueprint** |

## Quick Start

1. **Define the outcome** before building (Principle 1)
2. **Classify each step** as deterministic, agentic, or human-in-the-loop (Principle 2)
3. **Design exception paths** - assume systems will fail (Principle 3)
4. **Build governance in** - don't bolt it on (Principle 4)
5. **Make HITL explicit** - it's a design choice, not a fallback (Principle 5)
6. **Stay vendor-agnostic** - API-first integrations (Principle 6)
7. **Layer your architecture** - triggers, logic, actions, orchestration (Principle 7)

## Usage

### For New Workflows
Use `TEMPLATE.md` as a fill-in-the-blanks starting point.

### For M365 Security Incidents
Use `M365_INCIDENT_TRIAGE_BLUEPRINT.md` directly - it's production-ready with:
- Complete step classification matrix (D/A/H)
- 4-layer architecture with sub-stories
- Approval gate configurations with timeouts
- Exception handling matrix
- Immutable audit record schema

## Sources

- [Seven principles of intelligent workflow design](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [Tines Library - Incidents and Alerts](https://www.tines.com/library/use-cases/incidents-and-alerts/)
- [Tines Library - Security](https://www.tines.com/library/teams/security/)
