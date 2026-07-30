# Tines Intelligent Workflow Design Skill

## Overview
This skill provides enterprise-grade guidance for designing Tines workflows following the seven principles of intelligent workflow design.

## Files

| File | Purpose |
|-------|---------|
| [SKILL.md](SKILL.md) | The rulebook: seven principles, decision framework, anti-patterns |
| [TEMPLATE.md](TEMPLATE.md) | Workflow design template for new Tines Stories |
| [INCIDENT_TRIAGE_STORY.md](INCIDENT_TRIAGE_STORY.md) | Sample incident triage workflow for Microsoft Graph + Tines |

## Quick Start

1. **Define the outcome** before building (Principle 1)
2. **Classify each step** as deterministic, agentic, or human-in-the-loop (Principle 2)
3. **Design exception paths** - assume systems will fail (Principle 3)
4. **Build governance in** - don't bolt it on (Principle 4)
5. **Make HITL explicit** - it's a design choice, not a fallback (Principle 5)
6. **Stay vendor-agnostic** - API-first integrations (Principle 6)
7. **Layer your architecture** - triggers, logic, actions, orchestration (Principle 7)

## Usage

### Using the Skill
Reference this skill when designing any Tines Story. Apply the decision framework to each step.

### Using the Template
1. Copy `TEMPLATE.md` for each new workflow
2. Complete Section 1 (Business Outcome) before anything else
3. Classify each step in Section 2
4. Design layers in Section 3
5. Add HITL checkpoints in Section 4
6. Document exceptions in Section 5
7. Verify with Section 8 checklist

### Using the Sample Story
The incident triage story demonstrates:
- Microsoft Graph enrichment integration
- Severity-based routing
- Multi-tier approval gates
- Exception handling
- Audit logging

## Principles Source
Based on [Intelligent workflow design: seven principles for enterprise teams](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
