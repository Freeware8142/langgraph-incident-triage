# Incident Triage Story Outline

## Production Incident Triage Workflow for Microsoft Graph + Tines Integration

### Business Outcome
**Reduce mean time to respond (MTTR) for security incidents by 60%** while ensuring appropriate human oversight for high-risk remediation actions.

---

## Story Overview

```
Story Name: Incident Triage with Microsoft Graph Enrichment
Trigger: Security alert from SIEM/EDR → Webhook
Target Systems: Microsoft Graph, Tines Case Management, IT Service Desk
Risk Profile: Medium-High (involves user data and remediation actions)
```

---

## Library-Inspired Patterns Used

| Pattern | Implementation | Source |
|---------|----------------|--------|
| **AI-driven case creation** | AI Agent generates structured case summary from raw alert | Tines Incidents Library |
| **Multi-tool IOC enrichment** | Query Microsoft Graph + threat intel sources in parallel | Tines Security Library |
| **Rich notification with action buttons** | Slack/Teams with Approve/Deny/MoreInfo | Tines Slack interactivity |
| **Timeout escalation** | Auto-escalate if no response within N minutes | Tines Alert escalation |
| **Verification gate before action** | Require user confirmation before account actions | Tines Jamf pattern |
| **Immutable audit Record** | Tines Record with structured fields for compliance | Tines Case Management |
| **Incident comms channel** | Auto-create Slack channel + sync to Jira | Tines Incident comms |
| **Parallel enrichment** | Fire Graph API calls concurrently, aggregate | Tines Performance patterns |

---

## Layer 1: Trigger & Ingestion

### Trigger Configuration
- **Type:** Webhook (from SIEM/EDR)
- **Authentication:** API key or OAuth 2.0
- **Validation:** JSON schema validation on receipt

### Ingestion Steps
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 1.1 | Receive Alert | Deterministic | Low | Parse incoming webhook payload |
| 1.2 | Validate Schema | Deterministic | Low | Validate required fields present |
| 1.3 | Deduplicate | Deterministic | Low | Check against recent alerts (5 min window) using Tines Resource |
| 1.4 | Create Case | Deterministic | Low | Create Tines Case with alert metadata |
| 1.5 | Generate Case Summary | **Agentic** | Medium | AI Agent creates structured summary from raw alert data |

---

## Layer 2: Enrichment & Classification

### Microsoft Graph Integration (Parallel Enrichment Pattern)
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 2.1 | Get User Info | Deterministic | Low | Query Graph API for affected user |
| 2.2 | Get Sign-In Activity | Deterministic | Low | Retrieve recent sign-ins via Graph |
| 2.3 | Get Mail Activity | Deterministic | Low | Check for suspicious email activity |
| 2.4 | Get Device Status | Deterministic | Low | Query Intune/Defender for device health |
| 2.5 | Get Group Membership | Deterministic | Low | Check privileged group memberships |

**Library Pattern:** Parallel enrichment - fire all Graph API calls concurrently, aggregate results

### AI Classification
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 2.6 | Classify Incident Type | Agentic | Medium | LLM classifies: Phishing, Compromised Account, Malware, etc. |
| 2.7 | Assess Severity | Agentic | Medium | LLM assigns severity based on impact factors |
| 2.8 | Extract IOCs | Agentic | Medium | LLM extracts IPs, hashes, URLs from evidence |
| 2.9 | Log AI Inputs/Outputs | Deterministic | Low | Store prompts and responses in Tines Record for compliance |

### Decision Routing
```
Severity = Critical → Route to Step 3.3 (High-Risk Path)
Severity = High → Route to Step 3.2 (Medium-Risk Path)
Severity = Low/Medium → Route to Step 3.1 (Automated Response)
```

---

## Layer 3: Response Actions

### 3.1 Low-Risk Automated Response
**Trigger:** Severity = Low or Medium, Confidence > 80%

| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 3.1.1 | Create Ticket | Deterministic | Medium | Create ITSM ticket (ServiceNow/Jira) |
| 3.1.2 | Notify SOC | Deterministic | Low | Send Slack/Teams notification |
| 3.1.3 | Log to SIEM | Deterministic | Low | Close loop with detection system |
| 3.1.4 | Update Case | Deterministic | Low | Mark case as auto-resolved |

### 3.2 Medium-Risk Review Path
**Trigger:** Severity = High OR (Severity = Medium AND Confidence < 80%)

| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 3.2.1 | Prepare Review Context | Agentic | Low | Generate summary for analyst |
| 3.2.2 | **Rich Notification with Actions** | **HITL** | **Medium** | **Post to Slack with Approve/Deny/MoreInfo buttons** |
| 3.2.3 | Wait for Response | Deterministic | Low | Track response state with timeout |
| 3.2.4 | **Timeout Escalation** | Deterministic | Medium | If no response in 30 min, escalate to manager |
| 3.2.5 | Execute Remediation | Deterministic | Medium | Apply configured response action |

**Approval Gate 1 Configuration (Rich Notification Pattern):**
- **Approver:** On-call Security Analyst
- **Channel:** Slack/Teams with interactive buttons
- **Information at Gate:**
  - Incident summary and classification
  - User context and recent activity
  - Recommended remediation action
  - Affected assets and business impact
  - Quick action buttons: ✅ Approve | ❌ Deny | ℹ️ More Info
- **Timeout:** 30 minutes → Auto-escalate to manager
- **Library Pattern:** Slack interactivity + timeout escalation

### 3.3 High-Risk Approval Path
**Trigger:** Severity = Critical OR involves privileged accounts OR blast radius > 50 users

| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 3.3.1 | Prepare Executive Brief | Agentic | Medium | Generate severity briefing |
| 3.3.2 | **Create Incident Channel** | Deterministic | Low | Auto-create Slack channel for incident |
| 3.3.3 | **Manager Approval Gate** | **HITL** | **High** | **Rich notification + approval with timeout** |
| 3.3.4 | **Director Approval Gate** | **HITL** | **High** | **CISO/designate for critical + timeout** |
| 3.3.5 | **Verification Gate** | **HITL** | **High** | **Require user confirmation before action** |
| 3.3.6 | Execute Containment | Deterministic | High | Isolate user/device |
| 3.3.7 | Disable Account | Deterministic | High | Disable Azure AD account via Graph |

**Approval Gate 2 Configuration (Manager):**
- **Approver:** Security Manager
- **Channel:** Slack with interactive buttons
- **Information at Gate:**
  - Executive summary
  - IOCs and threat intelligence
  - Proposed containment actions
  - Business impact assessment
  - Quick action buttons: ✅ Approve | ❌ Deny | 🚨 War Room
- **Timeout:** 15 minutes → Auto-escalate to CISO
- **Library Pattern:** Rich notification + timeout escalation

**Approval Gate 3 Configuration (CISO):**
- **Approver:** CISO or delegate
- **Channel:** Slack direct message + backup phone notification
- **Information at Gate:**
  - Full incident timeline
  - All affected systems/users
  - Proposed eradication steps
  - Recovery plan
- **Timeout:** 30 minutes → Auto-deny if no response
- **Actions:** ✅ Full Response | ⚠️ Partial Response | ❌ Stand Down
- **Library Pattern:** Multi-channel notification + timeout escalation

**Verification Gate (User Confirmation Pattern):**
- **User:** Affected user (optional for speed)
- **Purpose:** Confirm if activity was authorized before executing destructive action
- **Channel:** Slack DM or email
- **Timeout:** 15 minutes → Proceed without confirmation (override for speed)
- **Library Pattern:** Verification before destructive action (inspired by Tines Jamf device lock)

---

## Layer 4: Integration Actions

### Tines Case Management (Immutable Audit Record Pattern)
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.1 | Update Case Status | Deterministic | Low | Set status: Investigating → Contained |
| 4.2 | Link Related Cases | Deterministic | Low | Connect related incidents |
| 4.3 | Add Timeline Events | Deterministic | Low | Record all actions with timestamps |
| 4.4 | Attach Evidence | Deterministic | Low | Link Graph API responses to case |
| 4.5 | Create Audit Record | Deterministic | Low | Immutable record: actor, target, action, before/after |

**Library Pattern:** Immutable audit Record with structured fields for compliance

### IT Service Desk Integration (Ticket Sync Pattern)
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.6 | Create Incident Ticket | Deterministic | Medium | Sync to ServiceNow/Jira |
| 4.7 | Assign Ticket | Deterministic | Medium | Route to appropriate team |
| 4.8 | **Sync Ticket Status** | Deterministic | Low | Loopback: keep Jira in sync with workflow state |

**Library Pattern:** Ticket sync with state loopback

### Notification Channels (Incident Comms Pattern)
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.9 | **Create Incident Channel** | Deterministic | Low | Auto-create Slack channel for critical incidents |
| 4.10 | Post Incident Details | Deterministic | Low | Post enriched incident summary |
| 4.11 | Sync Channel to Jira | Deterministic | Low | Archive Slack thread to Jira for long-term preservation |
| 4.12 | Notify Leadership | Deterministic | Low | Alert for Critical incidents |
| 4.13 | Email Affected User | Deterministic | Medium | Notify user of account action |

**Library Pattern:** Incident comms channel - auto-create Slack + sync to Jira

---

## Layer 5: Exception Handling & Audit

### Exception Handling (Catch-All Escalation Pattern)
| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Graph API rate limit | Check response code 429 | Wait and retry with exponential backoff (3 attempts) |
| User not found in Graph | Empty user object | Route to manual investigation queue |
| No on-call analyst available | Check schedule API | Escalate to manager |
| SIEM webhook retry | Check deduplication window | Log duplicate, skip processing |
| Approval timeout | Timer trigger | Auto-escalate per gate config |
| Graph API failure | Check response status | Continue with partial data, flag for review |
| Slack/Teams delivery failure | Check webhook response | Retry via email fallback |

**Library Pattern:** Catch-all escalation layer + timeout escalation

### Audit Logging (Immutable Record Pattern)
All actions logged with:
- Timestamp (ISO 8601)
- Actor (system/user)
- Action type
- Target resource
- Before/after state (for changes)
- Approval chain (for HITL steps)
- AI prompts and responses (for agentic steps)

**Tines Record Schema:**
```json
{
  "workflow": "incident-triage",
  "run_id": "uuid",
  "timestamp": "ISO8601",
  "actor": { "type": "system|user", "id": "..." },
  "action": { "type": "...", "target": "..." },
  "state": { "before": "...", "after": "..." },
  "approval_chain": [{ "approver": "...", "action": "...", "timestamp": "..." }],
  "ai_interaction": { "prompt": "...", "response": "..." }
}
```

**Library Pattern:** Immutable audit Record with structured fields

### Microsoft Graph Audit
- Store all Graph API calls with request/response
- Log Graph operation names (e.g., `user.disable`)
- Retain enrichment data for 90 days

---

## Story Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER: Webhook                        │
│                   (SIEM/EDR Alert)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: INGESTION                                        │
│  Validate → Deduplicate → Create Case                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: MICROSOFT GRAPH ENRICHMENT                      │
│  User Info ← Sign-Ins ← Mail Activity ← Device ← Groups   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2b: AI CLASSIFICATION                              │
│  Classify Type → Assess Severity → Extract IOCs           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Severity Check │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   [Low/Med]            [High]              [Critical]
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐      ┌──────────────┐     ┌──────────────┐
   │ Auto    │      │ Manager      │     │ Manager +    │
   │ Response│      │ Review       │     │ CISO Review  │
   └─────────┘      └──────────────┘     └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: RESPONSE ACTIONS                                 │
│  Tines Case → ITSM Ticket → Notifications                  │
│  + Remediation (Graph API / Disable Account)               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 4: AUDIT & ORCHESTRATION                           │
│  Timeline Events → Evidence Attachment → Audit Log          │
└─────────────────────────────────────────────────────────────┘
```

---

## Risk Tier Mapping

| Action | Risk Tier | Governance Required |
|--------|-----------|---------------------|
| Read Graph user info | Low | Logging only |
| Read sign-in logs | Low | Logging only |
| Create case | Low | Logging only |
| Send notification | Low | Logging only |
| Create ITSM ticket | Medium | RBAC + logging |
| Disable user account | **High** | **HITL + approval chain + verification gate** |
| Isolate device | **High** | **HITL + approval chain + verification gate** |
| Remove from groups | **High** | **HITL + approval chain** |

---

## Confidence-Based Routing

| Severity | Confidence | Path |
|----------|------------|------|
| Low | Any | Automated response |
| Medium | > 80% | Automated response |
| Medium | ≤ 80% | Manager review |
| High | Any | Manager review |
| Critical | Any | Manager + CISO approval |

---

## Governance Checklist

- [x] Audit trail captures all Graph API calls
- [x] HITL gates have information-rich context
- [x] Timeout policies configured per gate tier
- [x] Escalation path configured for timeouts
- [x] Approval chain documented and enforced
- [x] AI prompts and responses logged (immutable Record)
- [x] Before/after state captured for account changes
- [x] Exception paths designed and tested
- [x] Verification gate before destructive actions
- [x] Immutable audit Records created for compliance
- [x] Incident comms channel auto-created for critical
- [x] Slack thread synced to Jira for preservation

---

## Vendor-Agnostic Notes

| Current Integration | Abstraction Layer | Swap Path |
|--------------------|--------------------|------------|
| Microsoft Graph | Graph API wrapper story | Replace with Okta/Auth0 enrichment |
| ServiceNow | ITSM API story | Replace with Jira/Remedy |
| Slack | Webhook/API | Replace with Teams/PagerDuty |
| Tines Case | Case API | Native to platform |

---

## Reusable Sub-Stories (Layer Pattern)

The following sub-stories can be extracted and reused across multiple workflows:

| Sub-Story | Purpose | Inputs | Outputs |
|-----------|---------|--------|---------|
| **Microsoft Graph Enrichment** | Query user, sign-ins, mail, device, groups | User ID / Email | Structured enrichment data |
| **IOC Extraction Agent** | Extract IOCs from unstructured text | Raw alert text | IPs, hashes, URLs, domains |
| **Severity Classifier Agent** | Assign severity based on enrichment | Alert + enrichment data | Severity + confidence |
| **Approval Gate with Timeout** | Rich notification + escalation | Context, approvers, timeout | Approved/Denied/Escalated |
| **Immutable Audit Record** | Create compliance record | Action, actor, target, state | Tines Record ID |
| **Slack Incident Channel** | Create + populate channel | Incident details | Slack channel ID |
| **Ticket Sync Loopback** | Keep Jira in sync | Workflow state | Jira ticket update |

**Library Pattern:** Sub-story reuse for common operations

---

## Next Steps for Implementation

1. Create Graph API credential in Tines
2. Build enrichment sub-story (reusable across workflows)
3. Configure approval workflows with timeout policies
4. Set up audit log export to SIEM
5. Test exception paths with chaos scenarios
6. Document runbook for each approval tier
