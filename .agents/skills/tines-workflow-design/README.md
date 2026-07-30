# Tines Intelligent Workflow Design Skill

## Overview
This skill provides enterprise-grade guidance for designing Tines workflows following the seven principles of intelligent workflow design, enhanced with patterns from the Tines Library.

## Files

| File | Purpose |
|-------|---------|
| [SKILL.md](SKILL.md) | The rulebook: seven principles, decision framework, library patterns, production checklist |
| [TEMPLATE.md](TEMPLATE.md) | Workflow design template for new Tines Stories |
| [INCIDENT_TRIAGE_STORY.md](INCIDENT_TRIAGE_STORY.md) | Incident triage story outline with patterns |
| [M365_INCIDENT_TRIAGE_BLUEPRINT.md](M365_INCIDENT_TRIAGE_BLUEPRINT.md) | Strategic blueprint with rationale |
| [TINES_STORY_SPEC.md](TINES_STORY_SPEC.md) | **Ready-to-build Tines story specification** |

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
1. Start with `M365_INCIDENT_TRIAGE_BLUEPRINT.md` to understand the design rationale
2. Use `TINES_STORY_SPEC.md` to implement directly in Tines

## Key Documents

| Document | When to Use |
|----------|-------------|
| `M365_INCIDENT_TRIAGE_BLUEPRINT.md` | Design phase, stakeholder review |
| `TINES_STORY_SPEC.md` | Implementation phase, import into Tines |

## Sources

- [Seven principles of intelligent workflow design](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [Tines Library - Incidents and Alerts](https://www.tines.com/library/use-cases/incidents-and-alerts/)
- [Tines Library - Security](https://www.tines.com/library/teams/security/)
