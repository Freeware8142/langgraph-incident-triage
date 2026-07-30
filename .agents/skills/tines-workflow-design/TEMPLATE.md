# Tines Workflow Design Template

Use this template to design production-grade Tines Stories following the seven principles.

---

## Section 1: Business Outcome

**Workflow Name:** _________________________________

**Business Outcome:**
> What problem does this workflow solve? What is the measurable impact?

___________________________________________________________

**Success Metrics:**
- Metric 1: _________________________________
- Metric 2: _________________________________

**Stakeholders:**
- Owner: _________________________________
- Approvers: _________________________________

---

## Section 2: Step Classification

For each step, classify its execution mode:

| Step # | Step Name | Mode | Risk Tier | Governance |
|--------|-----------|------|-----------|------------|
| 1 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 2 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 3 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 4 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 5 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 6 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 7 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |
| 8 | | ☐ Deterministic ☐ Agentic ☐ HITL | ☐ Low ☐ Medium ☐ High | ☐ Yes ☐ No |

---

## Section 3: Layer Architecture

### Layer 1: Trigger/Event
**Trigger Type:** ☐ Webhook ☐ Schedule ☐ Manual ☐ API ☐ Event

**Trigger Configuration:**
```
_____________________________________________________________
```

### Layer 2: Logic/Decision
**Decision Points:**
1. _________________________________
2. _________________________________
3. _________________________________

**Routing Logic:**
```
_____________________________________________________________
```

### Layer 3: Action/Integration
**Systems Integrated:**
| System | API/Integration Type | Credential |
|--------|---------------------|------------|
| | | |
| | | |
| | | |

### Layer 4: Orchestration
**State Management:** _________________________________

**Error Handling Strategy:** _________________________________

---

## Section 4: Human-in-the-Loop Design

For each HITL checkpoint:

### HITL Checkpoint 1
**Purpose:** _________________________________
**Information at the Gate:**
```
- Alert context: _______________
- Affected assets: _______________
- Recommended action: _______________
- Risk assessment: _______________
```
**Timeout Policy:** ☐ Auto-deny ☐ Escalate ☐ Retry
**Timeout Duration:** _______________

### HITL Checkpoint 2 (if needed)
**Purpose:** _________________________________
**Information at the Gate:**
```
- Alert context: _______________
- Affected assets: _______________
- Recommended action: _______________
- Risk assessment: _______________
```
**Timeout Policy:** ☐ Auto-deny ☐ Escalate ☐ Retry
**Timeout Duration:** _______________

---

## Section 5: Exception Handling

| Step | Potential Failure | Recovery Action | Escalation Path |
|------|-------------------|----------------|-----------------|
| | | | |
| | | | |
| | | | |

**Catch-All Fallback:** _________________________________

---

## Section 6: Governance & Audit

### Required Audit Artifacts
- [ ] Who triggered the workflow
- [ ] Who approved each action
- [ ] What workflow executed
- [ ] What changed on each system
- [ ] Before/after state

### AI Governance (if applicable)
- [ ] Prompts stored with immutable audit trail
- [ ] Regulated data masked before AI processing
- [ ] AI outputs logged for review

---

## Section 7: Vendor Agnosticism Check

**Current Integrations:**
| Integration | Replacement Path |
|-------------|------------------|
| | |
| | |

**Abstraction Layer:** _________________________________

---

## Section 8: Design Review Checklist

- [ ] Business outcome clearly defined
- [ ] Each step has execution mode classification
- [ ] High-risk steps have HITL checkpoints
- [ ] Timeout policies defined for all HITL gates
- [ ] Exception paths designed and tested
- [ ] Audit trail covers all required artifacts
- [ ] Integrations are vendor-agnostic where possible
- [ ] Layers are decoupled (trigger, logic, action, orchestration)
- [ ] State preserved through failures
- [ ] Catch-all fallback designed

---

## Section 9: Tines Story Structure

```
┌─────────────────────────────────────────────────────────────┐
│ TRIGGER                                                      │
│ [Webhook/API/Schedule]                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: INGESTION & VALIDATION                             │
│ - Input validation (deterministic)                          │
│ - Schema checking (deterministic)                           │
│ - Deduplication (deterministic)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: ENRICHMENT & DECISION                             │
│ - Data enrichment (deterministic)                           │
│ - Classification (agentic)                                  │
│ - Risk scoring (agentic)                                    │
│ - Routing decision (deterministic)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Risk Check    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        [Low Risk]    [Med Risk]     [High Risk]
              │              │              │
              │              │              ▼
              │              │     ┌────────────────┐
              │              │     │  HITL GATE     │
              │              │     │  Human Review  │
              │              │     └────────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: ACTION & INTEGRATION                               │
│ - Create ticket (deterministic)                             │
│ - Send notification (deterministic)                         │
│ - Update system (deterministic)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: ORCHESTRATION & AUDIT                             │
│ - State management (deterministic)                         │
│ - Audit logging (deterministic)                            │
│ - Error handling (deterministic)                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage Instructions

1. **Complete Section 1** before writing any workflow logic
2. **Fill Section 2** for every step in the workflow
3. **Design each layer** following Section 3 architecture
4. **Add HITL checkpoints** using Section 4 template
5. **Document exceptions** in Section 5
6. **Verify governance** using Section 6 checklist
7. **Review vendor lock-in** using Section 7
8. **Complete Section 8** design review checklist
9. **Use Section 9** as a visual reference for Tines Story structure
