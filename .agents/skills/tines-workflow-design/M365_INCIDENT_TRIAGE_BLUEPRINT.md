# M365 Security Incident Triage Story Blueprint
## Production-Ready Tines Story for Microsoft 365 Security Events

---

## 1. Story Overview

### Story Metadata

| Field | Value |
|-------|-------|
| **Story Name** | `m365-incident-triage` |
| **Version** | 1.0.0 |
| **Author** | Security Engineering |
| **Last Updated** | 2026-07-30 |
| **Status** | Production Ready |

---

## 2. Business Outcome

> **Reduce mean time to respond (MTTR) for M365 security incidents by 60%** while ensuring appropriate human oversight for high-risk remediation actions.

**Measurable Goals:**
| Metric | Current | Target |
|--------|---------|--------|
| MTTR | Manual (~4 hours) | Automated (<1.5 hours) |
| Analyst triage time | 15 min/incident | <2 min/incident |
| False positive rate | TBD | <10% |

**Rationale:** Starting with the outcome ensures every design decision serves this goal. Without a measurable target, workflows become feature-rich but ineffective.

---

## 3. Trigger Configuration

### Primary Trigger: Webhook

```
Type: Webhook (HTTPS)
Source: Microsoft Sentinel / Defender / Purview
Authentication: API Key or OAuth 2.0
```

### Trigger Conditions

| Condition | Action |
|-----------|--------|
| Alert severity = High/Critical | Immediate processing |
| Alert severity = Medium | Batch processing (60s window) |
| Alert severity = Low | Scheduled processing (5 min window) |

**Rationale:** Prioritizing by severity ensures critical incidents get immediate attention while lower-priority alerts are batched to reduce resource consumption.

---

## 4. Inputs & Outputs

### Inputs

| Input | Type | Source | Required |
|-------|------|--------|----------|
| `alert_payload` | JSON | Webhook | Yes |
| `source_system` | String | Webhook header | Yes |
| `alert_id` | String | Payload | Yes |
| `affected_user_id` | String | Payload | Yes |
| `alert_type` | String | Payload | Yes |
| `alert_timestamp` | ISO8601 | Payload | Yes |

### Outputs

| Output | Destination | Purpose |
|-------|------------|---------|
| `tines_case_id` | Tines Case | Primary incident record |
| `enrichment_data` | Tines Resource | Cross-incident correlation |
| `audit_record_id` | Tines Record | Compliance audit trail |
| `itsm_ticket_id` | Jira/ServiceNow | Ticketing sync |
| `slack_channel_id` | Slack | Incident comms (critical only) |

---

## 5. Step Classification Matrix

### Mode Legend
- **D** = Deterministic (rule-based, machine-speed)
- **A** = Agentic (AI-assisted judgment)
- **H** = Human-in-the-Loop (manual approval required)

### Complete Step List

| # | Step Name | Mode | Risk | Rationale |
|---|-----------|------|------|----------|
| 1.1 | Receive Webhook | D | Low | Parse incoming alert |
| 1.2 | Validate Schema | D | Low | Ensure payload integrity |
| 1.3 | Check Deduplication | D | Low | Prevent duplicate processing |
| 1.4 | Create Tines Case | D | Low | Establish incident record |
| 2.1 | **Enrichment: User Profile** | D | Low | Parallel Graph call |
| 2.2 | **Enrichment: Sign-In Logs** | D | Low | Parallel Graph call |
| 2.3 | **Enrichment: Mail Activity** | D | Low | Parallel Graph call |
| 2.4 | **Enrichment: Device Status** | D | Low | Parallel Graph call |
| 2.5 | **Enrichment: Group Membership** | D | Low | Parallel Graph call |
| 2.6 | **Aggregate Enrichment** | D | Low | Combine parallel results |
| 3.1 | **Generate Case Summary** | A | Medium | AI creates structured narrative |
| 3.2 | **Classify Incident Type** | A | Medium | AI determines category |
| 3.3 | **Assess Severity** | A | Medium | AI assigns severity + confidence |
| 3.4 | **Extract IOCs** | A | Medium | AI extracts indicators |
| 3.5 | **Log AI Interaction** | D | Low | Immutable audit record |
| 4.1 | **Route: Low/Med Auto** | D | Low | Confidence >80% → auto |
| 4.2 | **Route: High Review** | H | Medium | Analyst approval gate |
| 4.3 | **Route: Critical Escalate** | H | High | Manager + CISO approval |
| 5.1 | **Rich Notification** | D | Low | Slack with action buttons |
| 5.2 | **Wait for Approval** | D | Low | Track response state |
| 5.3 | **Timeout Handler** | D | Medium | Escalate on no-response |
| 6.1 | **Verification Gate** | H | High | User confirmation for destructive |
| 6.2 | **Execute Remediation** | D | High | Apply response action |
| 7.1 | **Create ITSM Ticket** | D | Medium | Jira/ServiceNow sync |
| 7.2 | **Sync Ticket Status** | D | Low | Loopback state sync |
| 7.3 | **Create Audit Record** | D | Low | Immutable compliance record |
| 7.4 | **Update Case Timeline** | D | Low | Chronological event log |
| 7.5 | **Notify Stakeholders** | D | Low | Email/Slack notifications |

---

## 6. Layer Architecture

### Layer 1: Ingestion (Principle 3: Design for Exceptions)

```
┌─────────────────────────────────────────┐
│ TRIGGER: Webhook                        │
│ - Validate authentication                 │
│ - Parse payload                         │
│ - Check deduplication (5-min window)    │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ CREATE CASE                              │
│ - Initialize Tines Case                  │
│ - Set status: New                       │
│ - Link to source alert                  │
└─────────────────────────────────────────┘
```

**Exception Handling:**
| Failure | Detection | Recovery |
|---------|-----------|----------|
| Invalid payload | Schema validation fails | Log error, reject webhook |
| Duplicate alert | Hash check against Resource | Skip, acknowledge |
| Case creation fails | API error response | Retry 3x, escalate to dead-letter |

**Rationale:** Deduplication via stateful Resource prevents processing the same incident twice. The 5-minute window balances memory usage against duplicate prevention.

---

### Layer 2: Parallel Enrichment (Principle 7: Layer Architecture)

```
┌──────────────────────────────────────────────────────────┐
│ PARALLEL ENRICHMENT (All fire simultaneously)          │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ User Profile│  │ Sign-In    │  │ Mail        │  │
│  │ (Graph API) │  │ Logs       │  │ Activity    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
│                                                          │
│  ┌─────────────┐  ┌─────────────┐                     │
│  │ Device      │  │ Group       │                     │
│  │ Status      │  │ Membership   │                     │
│  └─────────────┘  └─────────────┘                     │
└──────────────────────────────────────────────────────────┘
         ↓ (aggregate)
┌──────────────────────────────────────────────────────────┐
│ AGGREGATE RESULTS                                        │
│ - Combine all enrichment data                           │
│ - Flag missing fields                                   │
│ - Calculate risk indicators                             │
└──────────────────────────────────────────────────────────┘
```

**Rationale:** Parallel enrichment minimizes latency. Each enrichment call is independent, so firing them concurrently reduces total enrichment time from ~5s (sequential) to ~1s.

**Graph API Endpoints:**
| Data | Endpoint | Permission |
|------|-----------|------------|
| User Profile | `GET /users/{id}` | User.Read |
| Sign-In Logs | `GET /auditLogs/signIns` | AuditLog.Read.All |
| Mail Activity | `GET /reports/getMailActivitySummary` | Reports.Read.All |
| Device Status | `GET /deviceManagement/managedDevices` | DeviceManagementManagedDevices.Read.All |
| Group Membership | `GET /users/{id}/memberOf` | User.Read |

---

### Layer 3: AI Classification (Principle 2: Match Execution Mode)

```
┌──────────────────────────────────────────────────────────┐
│ AI CLASSIFICATION                                       │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Case Summary    │ ← Structured narrative from raw   │
│  │ Generation      │   alert + enrichment               │
│  └─────────────────┘                                   │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Incident Type   │ ← Phishing, Compromise, Malware   │
│  │ Classification  │   Ransomware, Data Exfil            │
│  └─────────────────┘                                   │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Severity +      │ ← Low/Medium/High/Critical        │
│  │ Confidence      │   + confidence score (0-100%)       │
│  └─────────────────┘                                   │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ IOC Extraction  │ ← IPs, hashes, URLs, domains     │
│  └─────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
         ↓
┌──────────────────────────────────────────────────────────┐
│ LOG AI INTERACTION                                       │
│ - Store prompt + response in Tines Record               │
│ - Required for compliance audit                         │
└──────────────────────────────────────────────────────────┘
```

**Rationale:** AI classification handles the ambiguity that rules cannot encode. Classification over open vocabularies (incident types) and inference from unstructured evidence (enrichment data) require judgment that deterministic rules cannot provide.

**AI Prompt Template:**
```
Classify this M365 security incident:
- Alert type: {alert_type}
- Affected user: {user_display_name}
- Enrichment data: {enriched_data}
- Recent activity: {recent_signins}

Output JSON:
{
  "incident_type": "...",
  "severity": "...",
  "confidence": 0-100,
  "iocs": ["..."],
  "recommended_action": "..."
}
```

---

### Layer 4: Routing & Approval (Principle 5: Make HITL a Design Choice)

```
                    ┌─────────────────┐
                    │  Severity Check  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   [Low/Medium]         [High]             [Critical]
   Confidence > 80%      Any confidence    Any confidence
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐      ┌──────────────┐     ┌──────────────┐
   │ Auto    │      │ Slack with  │     │ Slack + CISO │
   │ Response│      │ Buttons +   │     │ + Verify +   │
   │         │      │ Timeout     │     │ Timeout      │
   └─────────┘      │ Escalation  │     │ Escalation   │
                    └──────────────┘     └──────────────┘
```

**Approval Gate Configuration:**

| Gate | Trigger | Approver | Timeout | Escalation | Auto-Action |
|------|---------|----------|---------|------------|-------------|
| **Analyst Review** | High severity OR Medium + Low confidence | On-call analyst | 30 min | → Manager | Deny |
| **Manager Approval** | Critical severity | Security manager | 15 min | → CISO | Escalate |
| **CISO Approval** | Critical + privileged account | CISO/designate | 30 min | → Auto-deny | Deny |
| **Verification** | Any destructive action | Affected user | 15 min | → Proceed | Proceed |

**Rationale:** Human oversight is mandatory for high-impact actions, but the workflow doesn't halt for low-risk incidents. Confidence-based routing ensures only uncertain cases reach reviewers, preventing approval fatigue.

---

### Layer 5: Response Actions (Principle 4: Build Governance In)

```
┌──────────────────────────────────────────────────────────┐
│ RESPONSE ACTIONS                                        │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Verification Gate│ ← "Did you authorize this?"      │
│  │ (Destructive)    │   (for account disable, etc.)   │
│  └─────────────────┘                                   │
│                    ↓                                    │
│  ┌─────────────────┐                                   │
│  │ Execute         │ ← Apply remediation via Graph API  │
│  │ Remediation     │   (disable, isolate, block)       │
│  └─────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

**Remediation Actions by Incident Type:**

| Incident Type | Action | API |
|---------------|--------|-----|
| Phishing | Block sender, mark email | `Set-MailboxJunkEmailConfiguration` |
| Compromised Account | Disable account, reset MFA | `Disable-MgUser`, `Revoke-MgUserSession` |
| Malware | Quarantine device | `Invoke-MgDeviceManage` |
| Data Exfil | Block sharing, revoke tokens | `Set-MgDriveItemPermission` |

---

### Layer 6: Orchestration & Audit (Principle 4: Governance Inside Workflow)

```
┌──────────────────────────────────────────────────────────┐
│ ORCHESTRATION                                           │
│                                                          │
│  ┌─────────────────┐  ┌─────────────────┐            │
│  │ Create ITSM     │  │ Sync Ticket     │            │
│  │ Ticket          │  │ Status         │            │
│  └─────────────────┘  └─────────────────┘            │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Create Immutable│  ← Structured audit record        │
│  │ Audit Record   │    with before/after state        │
│  └─────────────────┘                                   │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Update Case     │  ← Timeline of all events        │
│  │ Timeline        │    with timestamps                │
│  └─────────────────┘                                   │
│                                                          │
│  ┌─────────────────┐                                   │
│  │ Notify          │  ← Email/Slack to stakeholders   │
│  │ Stakeholders    │                                   │
│  └─────────────────┘                                   │
└──────────────────────────────────────────────────────────┘
```

---

## 7. Reusable Sub-Stories

### Sub-Story 1: Microsoft Graph Enrichment

```
Name: m365-graph-enrichment
Purpose: Reusable enrichment for any M365 user context
Trigger: Called by parent story
Inputs: user_id, enrichment_types[]
Outputs: enrichment_data{}

Actions:
  1. Parallel HTTP calls to Graph API
  2. Aggregate responses
  3. Return structured data
```

**Reuse Cases:** User onboarding audit, access review, compliance reporting

### Sub-Story 2: Approval Gate with Timeout

```
Name: approval-gate
Purpose: Rich notification + escalation
Trigger: Called by parent story
Inputs: context{}, approvers[], timeout_minutes
Outputs: {status: "approved"|"denied"|"escalated"|"timeout"}

Actions:
  1. Post Slack with action buttons
  2. Wait for response (tracked via Resource)
  3. Handle timeout → escalate
  4. Return decision
```

**Reuse Cases:** Any workflow requiring human approval

### Sub-Story 3: Immutable Audit Record

```
Name: audit-record
Purpose: Compliance-grade audit trail
Trigger: Called by any step requiring audit
Inputs: workflow_name, action, actor, target, before_state, after_state
Outputs: record_id

Actions:
  1. Build structured record
  2. Create Tines Record (immutable)
  3. Return record ID
```

**Reuse Cases:** All workflows requiring SOC2/ISO27001 compliance

### Sub-Story 4: Severity Classifier Agent

```
Name: m365-severity-classifier
Purpose: AI-based severity assessment
Trigger: Called after enrichment
Inputs: alert_data, enrichment_data
Outputs: {severity, confidence, reasoning}

Actions:
  1. Construct prompt with context
  2. Call LLM
  3. Parse response
  4. Log prompt/response to Record
```

**Reuse Cases:** Any triage workflow requiring severity scoring

---

## 8. Failure Paths

### Exception Handling Matrix

| Step | Failure Mode | Detection | Recovery |
|------|--------------|-----------|----------|
| 1.2 Schema validation | Invalid JSON | Try/catch | Reject, log error |
| 1.3 Deduplication | Resource unavailable | Connection error | Proceed without dedup |
| 2.x Graph enrichment | API rate limit (429) | Status code | Retry with backoff (3 attempts) |
| 2.x Graph enrichment | User not found | Empty response | Flag as "unknown", continue |
| 3.x AI classification | LLM timeout | Timeout error | Fall back to rule-based severity |
| 4.x Approval gate | No responder | Timeout trigger | Auto-escalate |
| 6.1 Verification | User unreachable | Timeout trigger | Proceed (security override) |
| 7.1 ITSM ticket | API error | HTTP error | Retry 3x, alert ops |

### Dead Letter Queue

```
Unprocessable alerts → Tines Resource: dead_letter_queue
├── reason: string
├── original_payload: object
├── attempted_at: timestamp
├── retry_count: number
└── status: "pending"|"resolved"
```

**Rationale:** Silent failures are worse than noisy ones. Dead-letter queue ensures no alert is ever lost and failures are visible for remediation.

---

## 9. Audit Record Schema

```json
{
  "record_type": "incident_triage_audit",
  "workflow_version": "1.0.0",
  "run_id": "uuid",
  "timestamp": "ISO8601",
  
  "trigger": {
    "source": "microsoft_sentinel|defender|purview",
    "alert_id": "string",
    "received_at": "ISO8601"
  },
  
  "actor": {
    "type": "system|user|ai",
    "identifier": "string"
  },
  
  "enrichment": {
    "duration_ms": number,
    "sources_queried": ["string"],
    "data_quality": "complete|partial|failed"
  },
  
  "classification": {
    "incident_type": "string",
    "severity": "low|medium|high|critical",
    "confidence": 0-100,
    "iocs": ["string"]
  },
  
  "approval_chain": [
    {
      "gate": "analyst|manager|ciso|verification",
      "approver": "email",
      "decision": "approved|denied|escalated|timeout",
      "decided_at": "ISO8601",
      "justification": "string"
    }
  ],
  
  "actions_taken": [
    {
      "action": "string",
      "target": "string",
      "before_state": "object",
      "after_state": "object",
      "executed_at": "ISO8601"
    }
  ],
  
  "ai_interaction": {
    "prompt": "string (truncated)",
    "response": "string (truncated)",
    "model": "string",
    "tokens_used": number
  },
  
  "outcome": {
    "status": "resolved|escalated|failed",
    "resolution": "string",
    "duration_seconds": number
  }
}
```

**Rationale:** Structured audit records enable compliance reporting, incident retrospectives, and AI model improvement through feedback loops.

---

## 10. Design Principles Summary

| Principle | Implementation |
|-----------|---------------|
| **1. Start with outcomes** | MTTR reduction goal drives every decision |
| **2. Match execution mode** | D for volume, A for judgment, H for risk |
| **3. Design for exceptions** | Dead-letter queue, retry logic, fallback severity |
| **4. Build governance in** | Immutable Records, approval chain, before/after state |
| **5. Make HITL explicit** | Confidence-based routing, timeout escalation |
| **6. Vendor-agnostic** | HTTP Request actions, abstracted Graph calls |
| **7. Layer architecture** | Reusable sub-stories, decoupled layers |

---

## 11. Implementation Checklist

- [ ] Create Graph API credential in Tines
- [ ] Configure webhook endpoint for Defender/Sentinel
- [ ] Build enrichment sub-story (test with known user)
- [ ] Configure AI agent with M365 incident prompts
- [ ] Set up approval workflow with Slack integration
- [ ] Create audit Record template
- [ ] Configure dead-letter queue Resource
- [ ] Test happy path with sample alert
- [ ] Test approval timeout escalation
- [ ] Test dead-letter handling
- [ ] Document runbook for each approval tier
- [ ] Train analysts on approval workflow

---

## 12. Library Pattern References

This blueprint incorporates these Tines Library patterns:

| Pattern | Section | Source Inspiration |
|---------|---------|-------------------|
| Parallel enrichment | Layer 2 | Engineering Library - Elastic monitoring |
| Rich notification with actions | Layer 4 | Security Library - Jamf device lock |
| Timeout escalation | Layer 4 | Incidents Library - Alert escalation |
| AI case generation | Layer 3 | Incidents Library - AI Agent |
| Immutable audit Record | Layer 6 | Case Management patterns |
| Incident comms channel | Layer 6 | Incidents Library - Slack + Jira |
| Stateful deduplication | Layer 1 | Resources tracking pattern |

---

*This blueprint is adapted from Tines Library patterns and the seven principles of intelligent workflow design. It is not copied verbatim from any specific Tines Story.*
