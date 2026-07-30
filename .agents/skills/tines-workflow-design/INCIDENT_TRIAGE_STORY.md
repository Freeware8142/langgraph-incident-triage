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
| 1.3 | Deduplicate | Deterministic | Low | Check against recent alerts (5 min window) |
| 1.4 | Create Case | Deterministic | Low | Create Tines Case with alert metadata |

---

## Layer 2: Enrichment & Classification

### Microsoft Graph Integration
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 2.1 | Get User Info | Deterministic | Low | Query Graph API for affected user |
| 2.2 | Get Sign-In Activity | Deterministic | Low | Retrieve recent sign-ins via Graph |
| 2.3 | Get Mail Activity | Deterministic | Low | Check for suspicious email activity |
| 2.4 | Get Device Status | Deterministic | Low | Query Intune/Defender for device health |
| 2.5 | Get Group Membership | Deterministic | Low | Check privileged group memberships |

### AI Classification
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 2.6 | Classify Incident Type | Agentic | Medium | LLM classifies: Phishing, Compromised Account, Malware, etc. |
| 2.7 | Assess Severity | Agentic | Medium | LLM assigns severity based on impact factors |
| 2.8 | Extract IOCs | Agentic | Medium | LLM extracts IPs, hashes, URLs from evidence |

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
| 3.2.2 | **Approval Gate** | **HITL** | **High** | **Analyst reviews and approves remediation** |
| 3.2.3 | Execute Remediation | Deterministic | Medium | Apply configured response action |

**Approval Gate 1 Configuration:**
- **Approver:** On-call Security Analyst
- **Information at Gate:**
  - Incident summary and classification
  - User context and recent activity
  - Recommended remediation action
  - Affected assets and business impact
- **Timeout:** 30 minutes → Escalate to manager
- **Actions:** Approve / Deny / Request More Info

### 3.3 High-Risk Approval Path
**Trigger:** Severity = Critical OR involves privileged accounts OR blast radius > 50 users

| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 3.3.1 | Prepare Executive Brief | Agentic | Medium | Generate severity briefing |
| 3.3.2 | **Manager Approval Gate** | **HITL** | **High** | **Security manager approves** |
| 3.3.3 | **Director Approval Gate** | **HITL** | **High** | **CISO/designate approves for critical** |
| 3.3.4 | Execute Containment | Deterministic | High | Isolate user/device |
| 3.3.5 | Disable Account | Deterministic | High | Disable Azure AD account via Graph |

**Approval Gate 2 Configuration (Manager):**
- **Approver:** Security Manager
- **Information at Gate:**
  - Executive summary
  - IOCs and threat intelligence
  - Proposed containment actions
  - Business impact assessment
- **Timeout:** 15 minutes → Auto-escalate to CISO
- **Actions:** Approve Containment / Deny / Request War Room

**Approval Gate 3 Configuration (CISO):**
- **Approver:** CISO or delegate
- **Information at Gate:**
  - Full incident timeline
  - All affected systems/users
  - Proposed eradication steps
  - Recovery plan
- **Timeout:** 30 minutes → Auto-deny if no response
- **Actions:** Approve Full Response / Partial Response / Stand Down

---

## Layer 4: Integration Actions

### Tines Case Management
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.1 | Update Case Status | Deterministic | Low | Set status: Investigating → Contained |
| 4.2 | Link Related Cases | Deterministic | Low | Connect related incidents |
| 4.3 | Add Timeline Events | Deterministic | Low | Record all actions with timestamps |
| 4.4 | Attach Evidence | Deterministic | Low | Link Graph API responses to case |

### IT Service Desk Integration
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.5 | Create Incident Ticket | Deterministic | Medium | Sync to ServiceNow/Jira |
| 4.6 | Assign Ticket | Deterministic | Medium | Route to appropriate team |
| 4.7 | Update Ticket Status | Deterministic | Low | Sync resolution status |

### Notification Channels
| Step | Name | Mode | Risk | Action |
|------|------|------|------|--------|
| 4.8 | Slack SOC Channel | Deterministic | Low | Post incident details |
| 4.9 | Teams Leadership | Deterministic | Low | Notify for Critical incidents |
| 4.10 | Email Affected User | Deterministic | Medium | Notify user of account action |

---

## Layer 5: Exception Handling & Audit

### Exception Handling
| Scenario | Detection | Recovery |
|----------|-----------|----------|
| Graph API rate limit | Check response code 429 | Wait and retry with exponential backoff |
| User not found in Graph | Empty user object | Route to manual investigation queue |
| No on-call analyst available | Check schedule API | Escalate to manager |
| SIEM webhook retry | Check deduplication window | Log duplicate, skip processing |
| Approval timeout | Timer trigger | Auto-escalate per gate config |

### Audit Logging
All actions logged with:
- Timestamp (ISO 8601)
- Actor (system/user)
- Action type
- Target resource
- Before/after state (for changes)
- Approval chain (for HITL steps)

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
| Disable user account | **High** | **HITL + approval chain** |
| Isolate device | **High** | **HITL + approval chain** |
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
- [x] Approval chain documented and enforced
- [x] AI prompts and responses logged
- [x] Before/after state captured for account changes
- [x] Exception paths tested and documented

---

## Vendor-Agnostic Notes

| Current Integration | Abstraction Layer | Swap Path |
|--------------------|--------------------|------------|
| Microsoft Graph | Graph API wrapper story | Replace with Okta/Auth0 enrichment |
| ServiceNow | ITSM API story | Replace with Jira/Remedy |
| Slack | Webhook/API | Replace with Teams/PagerDuty |
| Tines Case | Case API | Native to platform |

---

## Next Steps for Implementation

1. Create Graph API credential in Tines
2. Build enrichment sub-story (reusable across workflows)
3. Configure approval workflows with timeout policies
4. Set up audit log export to SIEM
5. Test exception paths with chaos scenarios
6. Document runbook for each approval tier
