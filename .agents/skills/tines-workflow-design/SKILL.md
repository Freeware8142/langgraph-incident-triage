# Tines Intelligent Workflow Design Skill

## Purpose
Design production-grade Tines workflows using the **seven principles of intelligent workflow design** for enterprise teams.

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

**Principle:** Business logic belongs in workflow components, not integration infrastructure.

**Benefit:** Swapping a SIEM or ticketing system doesn't force a rewrite of the entire flow.

---

## Decision Framework for Tines Story Design

When designing a Tines Story, evaluate each step:

```
Step: [Name]
├── Mode: [Deterministic | Agentic | Human-in-the-Loop]
├── Risk Tier: [Low | Medium | High]
├── Governance Required: [Yes | No]
├── Exception Handling: [What can fail? What happens?]
└── Integration: [Which systems? Vendor-agnostic?]
```

## Risk Tiers

| Tier | Criteria | Governance |
|------|----------|------------|
| **Low** | Read-only, no system changes, reversible | Basic logging |
| **Medium** | Creates records, sends notifications, modifies non-critical data | RBAC + activity logging |
| **High** | Financial transactions, system config changes, user data access | Formal pre-deployment approval + mandatory HITL |

## Anti-Patterns to Avoid

1. Starting with tool selection instead of outcome definition
2. Applying one execution mode uniformly
3. Happy-path assumptions about system availability and data quality
4. Governance as a separate compliance workflow
5. Approval workflows without confidence-based routing
6. Vendor-specific integrations without abstraction
7. Monolithic workflows where all concerns are coupled

## Key Tines Concepts

- **Story:** Tines' term for a workflow
- **Action:** Individual step in a Story (HTTP Request, AI, Approval, etc.)
- **Trigger:** Event source that starts a Story (webhook, schedule, manual)
- **Credential:** Stored authentication for integrations
- **Record:** Audit trail and state management
- **Case:** Container for related incidents/work items
- **Change Control:** Governance layer for Story modifications

## Sources

- [Intelligent workflow design: seven principles for enterprise teams](https://www.tines.com/blog/intelligent-workflow-design-7-principles-for-enterprise-teams/)
- [What is an intelligent workflow? The enterprise blueprint](https://www.tines.com/blog/what-is-an-intelligent-workflow-the-enterprise-blueprint/)
- [Tines Documentation](https://docs.tines.com/en/)
