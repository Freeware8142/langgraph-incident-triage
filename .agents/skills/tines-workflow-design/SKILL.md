# Tines Intelligent Workflow Design Skill

## Purpose
Design production-grade Tines workflows using the **seven principles of intelligent workflow design** for enterprise teams, enhanced with patterns from the Tines Library.

## The Seven Principles

### 1. Start with Outcomes, Not Tools
Every workflow begins with a defined **business outcome**, not platform features.

**Questions to answer before building:**
- What problem are we solving? (e.g., "reduce mean time to respond for phishing incidents")
- What capabilities are required?
- What is the capability gap?

**Framework:**
```
Business Outcome → Required Capabilities → Workflow Design → Platform Selection
```

**Anti-pattern:** Starting with "we'll use Tines to do X" without defining X's value.

---

### 2. Match Execution Mode to Decision Complexity

Three execution modes exist on a spectrum:

| Mode | When to Use | Examples |
|------|-------------|----------|
| **Deterministic** | Fully documented process, structured inputs, high cost of wrong output | Ingestion, enrichment, standardized responses |
| **Agentic (AI)** | Workflow structure defined, but individual decisions need judgment | Summarization, classification over open vocabularies, reasoning through ambiguous evidence |
| **Human-in-the-Loop** | Uncertainty, risk, or regulatory constraints exceed thresholds | Financial transactions, system config changes, high-impact actions |

**Gate test (Microsoft):** If every valid output can be enumerated in unit tests → deterministic. If validation requires simple rules → deterministic.

---

### 3. Design for Exceptions

Do not handle errors—**expect them**.

**Patterns:**
- **Catch-all escalation layer:** Every escalation policy needs an always-on fallback
- **State preservation:** Preserve workflow state through failures
- **Dead letter handling:** Route failed steps to review queue
- **Timeout policies:** Set at workflow level; escalate or auto-deny based on risk tier
- **User verification gates:** Require confirmation before destructive actions (inspired by Tines Jamf device lock pattern)

**Anti-pattern:** Assuming someone is always on-call, systems are healthy, data is complete.

---

### 4. Build Governance Into the Workflow

Governance must operate **inside** the workflow, not alongside it.

**Required audit artifacts:**
- Who triggered the workflow
- Who approved each action
- What workflow executed
- What changed on each system
- Before/after state

**For AI actions:**
- Store prompts and responses with immutable audit trails
- Mask regulated data before reaching AI models
- Apply same governance as deterministic actions

**Library-inspired pattern:** Use Tines Records for immutable audit logging with structured fields.

---

### 5. Make Human-in-the-Loop a Design Choice

Human-in-the-loop is not a fallback—it's a **design-time decision**.

**Four decisions at design time:**

1. **State preservation:** Workflow must preserve state while waiting for human input
2. **Information at the gate:** Context determines if approval is genuine oversight or click-through
3. **Timeout policy:**
   - Auto-deny for irreversible high-impact actions
   - Escalate for time-sensitive decisions
   - Retry for lower-stakes reviews
4. **Confidence-based routing:** Only low-confidence or high-risk decisions reach human review

**Library-inspired patterns:**
- **Slack interactivity prompts:** Send rich context to approver, take action based on response
- **Verification before action:** Require MFA/confirmation before destructive operations
- **Escalation with timeout:** If no response in X minutes, escalate to next level

**Anti-pattern:** Approval workflows where reviewers develop click-through habits due to over-familiarity.

---

### 6. Treat Integration as Vendor-Agnostic by Default

**API-first integration model:** If it has an API, connect to it.

**Patterns:**
- Use HTTP Request Actions for REST, GraphQL, SOAP
- Model business logic in workflow components, not integration infrastructure
- Avoid proprietary connector ecosystems that create lock-in

**Why it matters:** Migration friction becomes visible when you need to swap systems.

---

### 7. Architect in Layers So Workflows Can Evolve

**Four layers with independent responsibilities:**

| Layer | Responsibility | Independence Goal |
|-------|----------------|-------------------|
| **Trigger/Event** | Detects conditions, emits events | Decoupled from what happens next |
| **Logic/Decision** | Business rules, routing, enrichment | Decoupled from how actions execute |
| **Action/Integration** | Executes against external systems | Decoupled from why it was invoked |
| **Orchestration** | Coordinates sequence, state, error handling | Decoupled from individual components |

**Library-inspired pattern:** Build reusable **sub-stories** for common operations (enrichment, notification, ticketing) that can be shared across workflows.

**Principle:** Business logic belongs in workflow components, not integration infrastructure.

**Benefit:** Swapping a SIEM or ticketing system doesn't force a rewrite of the entire flow.

---

## Library-Inspired Design Patterns

### Enrichment Patterns

| Pattern | Description | Source |
|---------|-------------|--------|
| **Multi-tool IOC enrichment** | Query multiple threat intel sources (VirusTotal, CrowdStrike, PolySwarm) in parallel | Tines Security Library |
| **AI-driven case creation** | Use AI Agent to generate structured cases from raw alerts | Tines Incidents Library |
| **Stateful enrichment** | Cache enrichment results in Resources for cross-run correlation | Tines Tracking State pattern |

### Approval & Verification Patterns

| Pattern | Description | Source |
|---------|-------------|--------|
| **Rich notification with action buttons** | Post to Slack/Teams with Approve/Deny/MoreInfo options | Tines Slack interactivity |
| **Verification gate before destructive action** | Require MFA or confirmation (e.g., Duo push) before lockout | Tines Jamf device lock |
| **Timeout escalation** | Escalate if no response within N minutes | Tines Alert escalation pattern |
| **User acknowledgment loop** | Ask user to confirm if they recognize activity | Tines User acknowledgment |

### Orchestration Patterns

| Pattern | Description | Source |
|---------|-------------|--------|
| **Incident comms channel** | Auto-create Slack channel + sync to Jira for long-term preservation | Tines Incident comms |
| **State tracking across Stories** | Use Resources to track metrics across Story runs | Tines Resources pattern |
| **Parallel enrichment with aggregation** | Fire multiple enrichment requests concurrently, aggregate results | Tines Performance patterns |

### Governance Patterns

| Pattern | Description | Source |
|---------|-------------|--------|
| **Immutable audit Record** | Create Tines Record for each action with actor, target, before/after | Tines Case Management |
| **AI prompt/response logging** | Store LLM inputs and outputs for compliance | Tines AI Governance |
| **Ticket sync with state loopback** | Keep ITSM ticket in sync with workflow state changes | Tines Ticket sync |

---

## Decision Framework for Tines Story Design

When designing a Tines Story, evaluate each step:

```
Step: [Name]
├── Mode: [Deterministic | Agentic | Human-in-the-Loop]
├── Risk Tier: [Low | Medium | High]
├── Governance Required: [Yes | No]
├── Exception Handling: [What can fail? What happens?]
├── Integration: [Which systems? Vendor-agnostic?]
└── Library Pattern: [If applicable, reference source]
```

## Risk Tiers

| Tier | Criteria | Governance |
|------|----------|------------|
| **Low** | Read-only, no system changes, reversible | Basic logging |
| **Medium** | Creates records, sends notifications, modifies non-critical data | RBAC + activity logging |
| **High** | Financial transactions, system config changes, user data access | Formal pre-deployment approval + mandatory HITL + verification gate |

## Anti-Patterns to Avoid

1. Starting with tool selection instead of outcome definition
2. Applying one execution mode uniformly
3. Happy-path assumptions about system availability and data quality
4. Governance as a separate compliance workflow
5. Approval workflows without confidence-based routing
6. Vendor-specific integrations without abstraction
7. Monolithic workflows where all concerns are coupled
8. Missing timeout/escalation for approval gates
9. No verification before destructive actions

## Key Tines Concepts

- **Story:** Tines' term for a workflow
- **Action:** Individual step in a Story (HTTP Request, AI, Approval, etc.)
- **Trigger:** Event source that starts a Story (webhook, schedule, manual)
- **Credential:** Stored authentication for integrations
- **Record:** Immutable audit trail and state management
- **Case:** Container for related incidents/work items
- **Resource:** Cross-story state storage
- **Change Control:** Governance layer for Story modifications

## Production Checklist

- [ ] Business outcome defined and measurable
- [ ] Each step has execution mode classification
- [ ] High-risk steps have HITL checkpoints with rich context
- [ ] Verification gate before destructive actions
- [ ] Timeout policies defined for all HITL gates
- [ ] Escalation path configured for timeouts
- [ ] Exception paths designed and tested
- [ ] Audit trail covers all required artifacts
- [ ] AI prompts/responses logged (if using Agentic mode)
- [ ] Integrations are vendor-agnostic where possible
- [ ] Layers are decoupled (trigger, logic, action, orchestration)
- [ ] State preserved through failures
- [ ] Catch-all fallback designed
- [ ] Reusable sub-stories identified for common patterns

## Sources

- [Intelligent workflow design: seven principles for enterprise teams](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [What is an intelligent workflow? The enterprise blueprint](https://www.tines.com/blog/what-is-an-intelligent-workflow-the-enterprise-blueprint/)
- [Tines Library - Incidents and Alerts](https://www.tines.com/library/use-cases/incidents-and-alerts/)
- [Tines Library - Security](https://www.tines.com/library/teams/security/)
- [Tines Documentation](https://docs.tines.com/en/)
