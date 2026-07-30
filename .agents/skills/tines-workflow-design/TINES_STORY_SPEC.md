# M365 Incident Triage - Tines Story Specification
## Production-Ready Story Spec for Implementation

---

## Document Metadata

| Field | Value |
|-------|-------|
| **Spec Version** | 1.0.0 |
| **Blueprint Source** | `M365_INCIDENT_TRIAGE_BLUEPRINT.md` |
| **Status** | Ready for Review |
| **Created** | 2026-07-30 |

---

## 1. Story Overview

### Basic Information

```yaml
story_name: m365-incident-triage
description: >
  Production incident triage workflow for Microsoft 365 security events.
  Receives alerts from Defender/Sentinel, enriches via Microsoft Graph API,
  classifies severity with AI, and routes to appropriate response path
  with human approval gates for high-risk actions.
version: "1.0"
folder_id: "${FOLDER_ID}"  # Replace with Tines folder ID
team_id: "${TEAM_ID}"      # Replace with Tines team ID
```

### Business Outcome

> **Reduce MTTR for M365 security incidents by 60%** while ensuring appropriate human oversight for high-risk remediation actions.

**Target Metrics:**
| Metric | Target |
|--------|--------|
| MTTR | <1.5 hours (from 4 hours) |
| Analyst time per incident | <2 minutes |
| False positive rate | <10% |

---

## 2. Credentials & Resources

### Required Credentials

```yaml
credentials:
  - name: microsoft_graph_client_id
    type: text
    description: Azure AD application client ID for Graph API
    placeholder: "${MS_GRAPH_CLIENT_ID}"
    
  - name: microsoft_graph_client_secret
    type: text
    description: Azure AD application client secret
    placeholder: "${MS_GRAPH_CLIENT_SECRET}"
    
  - name: microsoft_graph_tenant_id
    type: text
    description: Azure AD tenant ID
    placeholder: "${MS_GRAPH_TENANT_ID}"
    
  - name: tines_api_key
    type: text
    description: Tines API key for sub-story calls
    placeholder: "${TINES_API_KEY}"
    
  - name: slack_webhook_url
    type: text
    description: Slack webhook for notifications
    placeholder: "${SLACK_WEBHOOK_URL}"
    
  - name: jira_api_token
    type: text
    description: Jira API token
    placeholder: "${JIRA_API_TOKEN}"
```

### Required Resources

```yaml
resources:
  - name: deduplication_cache
    type: key_value
    description: Tracks recently processed alerts to prevent duplicates
    retention: 5 minutes
    
  - name: approval_states
    type: key_value
    description: Tracks approval gate responses and timeout states
    retention: 60 minutes
    
  - name: dead_letter_queue
    type: key_value
    description: Failed/unprocessable alerts for manual review
    retention: 30 days
```

---

## 3. Trigger Configuration

### Primary Trigger

```yaml
trigger:
  type: webhook
  name: m365_security_alerts
  authentication:
    type: api_key
    header: X-API-Key
    credential: sentinel_webhook_key
    
  payload_schema:
    required:
      - alert_id
      - alert_type
      - severity
      - affected_user_id
      - timestamp
    optional:
      - source_system
      - raw_evidence
      - tags
```

### Trigger Filters

```yaml
trigger_filters:
  - name: severity_filter
    condition: severity IN ["Low", "Medium", "High", "Critical"]
    
  - name: alert_type_whitelist
    condition: >
      alert_type IN [
        "credentialTheft",
        "malware",
        "phishing", 
        "dataExfiltration",
        "privilegeEscalation",
        "lateralMovement"
      ]
```

---

## 4. Inputs & Outputs

### Input Payload Schema

```json
{
  "alert_id": "string (required)",
  "alert_type": "string (required)",
  "severity": "string (required): Low|Medium|High|Critical",
  "affected_user_id": "string (required)",
  "affected_user_email": "string (optional)",
  "timestamp": "ISO8601 (required)",
  "source_system": "string (optional): defender|sentinel|purview",
  "raw_evidence": "object (optional)",
  "tags": ["string"] 
}
```

### Output Schema

```json
{
  "run_id": "uuid",
  "tines_case_id": "string",
  "enrichment_data": {
    "user_profile": "object",
    "signin_logs": "array",
    "mail_activity": "array", 
    "device_status": "object",
    "group_membership": "array"
  },
  "classification": {
    "incident_type": "string",
    "severity": "string",
    "confidence": "number (0-100)",
    "iocs": ["string"]
  },
  "approval_chain": [{
    "gate": "string",
    "approver": "string",
    "decision": "string",
    "timestamp": "ISO8601"
  }],
  "actions_taken": [{
    "action": "string",
    "target": "string",
    "result": "string"
  }],
  "audit_record_id": "string",
  "itsm_ticket_id": "string",
  "outcome": {
    "status": "resolved|escalated|failed",
    "duration_seconds": "number"
  }
}
```

---

## 5. Action Specification

### Action List with Dependencies

```yaml
actions:
  
  # ==================== LAYER 1: INGESTION ====================
  
  - id: 1.1
    name: receive_webhook
    type: trigger
    mode: deterministic
    description: Receive and parse incoming webhook payload
    outputs:
      - alert_id
      - alert_type
      - severity
      - affected_user_id
      - timestamp
    depends_on: []
      
  - id: 1.2
    name: validate_schema
    type: event_transform
    mode: deterministic
    description: Validate required fields present
    outputs:
      - validation_status
      - validation_errors
    depends_on: [1.1]
    error_action: reject_alert
      
  - id: 1.3
    name: check_deduplication
    type: http_request
    mode: deterministic
    description: Check Resource for recent duplicate
    outputs:
      - is_duplicate
      - cache_key
    depends_on: [1.2]
    resource: deduplication_cache
    conditions:
      - if is_duplicate == true:
          skip_to: 9.1  # Log duplicate, end
      
  - id: 1.4
    name: create_tines_case
    type: http_request
    mode: deterministic
    description: Create Tines Case for incident
    outputs:
      - case_id
      - case_url
    depends_on: [1.3]
    api_call:
      method: POST
      endpoint: "${TINES_API_URL}/cases"
      body:
        name: "M365 Incident: ${alert_type} - ${affected_user_id}"
        folder_id: "${FOLDER_ID}"
        fields:
          alert_id: "${alert_id}"
          alert_type: "${alert_type}"
          severity: "${severity}"
          affected_user: "${affected_user_id}"
          
  - id: 1.5
    name: log_to_deduplication_cache
    type: http_request
    mode: deterministic
    description: Record alert ID to prevent duplicates
    depends_on: [1.4]
    resource: deduplication_cache
    action: set
    ttl: 300  # 5 minutes
    
  # ==================== LAYER 2: ENRICHMENT ====================
  
  - id: 2.1
    name: get_graph_token
    type: http_request
    mode: deterministic
    description: Obtain Graph API access token
    outputs:
      - access_token
    depends_on: [1.4]
    api_call:
      method: POST
      endpoint: "https://login.microsoftonline.com/${MS_GRAPH_TENANT_ID}/oauth2/v2.0/token"
      body:
        client_id: "${MS_GRAPH_CLIENT_ID}"
        client_secret: "${MS_GRAPH_CLIENT_SECRET}"
        scope: "https://graph.microsoft.com/.default"
        grant_type: client_credentials
        
  - id: 2.2
    name: enrich_user_profile
    type: http_request
    mode: deterministic
    description: Query Graph for user profile
    outputs:
      - user_profile
    depends_on: [2.1]
    parallel_group: graph_enrichment
    api_call:
      method: GET
      endpoint: "https://graph.microsoft.com/v1.0/users/${affected_user_id}"
      headers:
        Authorization: "Bearer ${access_token}"
        
  - id: 2.3
    name: enrich_signin_logs
    type: http_request
    mode: deterministic
    description: Get recent sign-in activity
    outputs:
      - signin_logs
    depends_on: [2.1]
    parallel_group: graph_enrichment
    api_call:
      method: GET
      endpoint: >
        https://graph.microsoft.com/v1.0/auditLogs/signIns?$filter=
        userPrincipalName eq '${affected_user_email}'&$top=10&$orderBy=createdDateTime desc
      headers:
        Authorization: "Bearer ${access_token}"
        
  - id: 2.4
    name: enrich_mail_activity
    type: http_request
    mode: deterministic
    description: Check mail activity for suspicious patterns
    outputs:
      - mail_activity
    depends_on: [2.1]
    parallel_group: graph_enrichment
    api_call:
      method: GET
      endpoint: >
        https://graph.microsoft.com/v1.0/reports/getMailActivitySummary
        ($period=7D)?$format=application/json
      headers:
        Authorization: "Bearer ${access_token}"
        
  - id: 2.5
    name: enrich_device_status
    type: http_request
    mode: deterministic
    description: Get managed device status
    outputs:
      - device_status
    depends_on: [2.1]
    parallel_group: graph_enrichment
    api_call:
      method: GET
      endpoint: >
        https://graph.microsoft.com/v1.0/users/${affected_user_id}
        /managedDevices?$top=5
      headers:
        Authorization: "Bearer ${access_token}"
        
  - id: 2.6
    name: enrich_group_membership
    type: http_request
    mode: deterministic
    description: Check privileged group memberships
    outputs:
      - group_membership
    depends_on: [2.1]
    parallel_group: graph_enrichment
    api_call:
      method: GET
      endpoint: >
        https://graph.microsoft.com/v1.0/users/${affected_user_id}
        /memberOf?$top=50
      headers:
        Authorization: "Bearer ${access_token}"
        
  - id: 2.7
    name: aggregate_enrichment
    type: event_transform
    mode: deterministic
    description: Combine all enrichment results
    outputs:
      - enrichment_complete
      - enrichment_data
      - missing_data_flags
    depends_on: 
      - 2.2
      - 2.3
      - 2.4
      - 2.5
      - 2.6
    parallel_wait: graph_enrichment
    
  # ==================== LAYER 3: AI CLASSIFICATION ====================
  
  - id: 3.1
    name: generate_case_summary
    type: ai_agent
    mode: agentic
    description: AI generates structured narrative from alert + enrichment
    outputs:
      - case_summary
      - summary_confidence
    depends_on: [2.7]
    model: gpt-4
    system_prompt: |
      You are a security analyst summarizing M365 incidents.
      Create a concise narrative from the alert and enrichment data.
      Focus on: what happened, who was affected, potential impact.
    user_prompt: |
      Alert: {alert_type} - Severity: {severity}
      User: {affected_user_id}
      Enrichment: {enrichment_data}
      Raw Evidence: {raw_evidence}
      
  - id: 3.2
    name: classify_incident_type
    type: ai_agent
    mode: agentic
    description: AI classifies incident into category
    outputs:
      - incident_type
      - type_confidence
    depends_on: [3.1]
    model: gpt-4
    system_prompt: |
      Classify this M365 security incident into one of:
      - credentialTheft
      - malware
      - phishing
      - dataExfiltration
      - privilegeEscalation
      - lateralMovement
      - falsePositive
      Return JSON: {"incident_type": "...", "confidence": 0-100}
    user_prompt: "{case_summary} + {enrichment_data}"
    
  - id: 3.3
    name: assess_severity
    type: ai_agent
    mode: agentic
    description: AI assesses severity with confidence score
    outputs:
      - assessed_severity
      - severity_confidence
      - risk_factors
    depends_on: [3.2]
    model: gpt-4
    system_prompt: |
      Assess severity of this M365 incident considering:
      - User role and access level
      - Recent suspicious activity
      - Potential blast radius
      - Business impact
      
      Return JSON:
      {
        "severity": "Low|Medium|High|Critical",
        "confidence": 0-100,
        "risk_factors": ["..."]
      }
    user_prompt: "{enrichment_data} + {case_summary}"
      
  - id: 3.4
    name: extract_iocs
    type: ai_agent
    mode: agentic
    description: AI extracts indicators of compromise
    outputs:
      - iocs
      - ioc_types
    depends_on: [3.3]
    model: gpt-4
    system_prompt: |
      Extract IOCs from this incident.
      Return JSON:
      {
        "iocs": [
          {"type": "ip|hash|domain|url|file", "value": "...", "context": "..."}
        ]
      }
    user_prompt: "{raw_evidence} + {enrichment_data}"
    
  - id: 3.5
    name: log_ai_interaction
    type: http_request
    mode: deterministic
    description: Store AI prompts/responses for compliance
    outputs:
      - ai_log_id
    depends_on:
      - 3.1
      - 3.2
      - 3.3
      - 3.4
    api_call:
      method: POST
      endpoint: "${TINES_API_URL}/records"
      body:
        record_type: ai_interaction_log
        workflow: m365-incident-triage
        run_id: "${RUN_ID}"
        prompts: ["${3.1.prompt}", "${3.2.prompt}", "${3.3.prompt}", "${3.4.prompt}"]
        responses: ["${3.1.response}", "${3.2.response}", "${3.3.response}", "${3.4.response}"]
        timestamps: ["${3.1.completed_at}", ...]
        
  # ==================== LAYER 4: ROUTING ====================
  
  - id: 4.1
    name: route_by_severity
    type: event_transform
    mode: deterministic
    description: Route based on severity and confidence
    depends_on: [3.5]
    conditions:
      - name: auto_response
        condition: >
          (assessed_severity IN ["Low", "Medium"]) AND 
          (severity_confidence > 80)
        skip_to: 5.1  # Auto response path
        
      - name: analyst_review
        condition: >
          (assessed_severity == "High") OR
          ((assessed_severity == "Medium") AND (severity_confidence <= 80))
        skip_to: 5.2  # Analyst approval
        
      - name: critical_escalation
        condition: assessed_severity == "Critical"
        skip_to: 5.3  # Manager + CISO approval
        
  # ==================== LAYER 5: RESPONSE PATHS ====================
  
  # Auto Response Path (Low/Medium + High Confidence)
  - id: 5.1
    name: auto_response_notification
    type: http_request
    mode: deterministic
    description: Notify SOC of auto-resolved incident
    depends_on: [4.1]
    path: auto_response
    api_call:
      method: POST
      endpoint: "${SLACK_WEBHOOK_URL}"
      body:
        text: "✅ M365 Incident Auto-Resolved"
        attachments:
          - color: good
            fields:
              - title: Incident Type
                value: "${incident_type}"
              - title: Severity
                value: "${assessed_severity}"
              - title: Affected User
                value: "${affected_user_id}"
              - title: Confidence
                value: "${severity_confidence}%"
                
  - id: 5.2
    name: analyst_approval_request
    type: http_request
    mode: human_lead
    description: Request analyst approval via Slack
    outputs:
      - approval_request_id
      - approval_channel
    depends_on: [4.1]
    path: analyst_review
    api_call:
      method: POST
      endpoint: "${SLACK_WEBHOOK_URL}"
      body:
        text: "🔔 M365 Incident Requires Review"
        blocks:
          - type: section
            text: "Incident: ${incident_type} - Severity: ${assessed_severity}"
          - type: section
            text: "User: ${affected_user_id}"
          - type: actions
            elements:
              - type: button
                text: Approve
                action_id: analyst_approve
              - type: button
                text: Deny
                action_id: analyst_deny
              - type: button
                text: More Info
                action_id: analyst_more_info
                
  - id: 5.3
    name: critical_approval_request
    type: http_request
    mode: human_lead
    description: Request manager + CISO approval for critical
    outputs:
      - manager_approval_id
      - ciso_approval_id
    depends_on: [4.1]
    path: critical_escalation
    # This triggers both approvals sequentially
    
  - id: 5.4
    name: wait_for_analyst_response
    type: event_receiver
    mode: deterministic
    description: Wait for analyst approval response
    outputs:
      - analyst_decision
      - decision_timestamp
    depends_on: [5.2]
    timeout_minutes: 30
    timeout_action: escalate_to_manager
    resource: approval_states
    
  - id: 5.5
    name: escalation_handler
    type: event_transform
    mode: deterministic
    description: Handle timeout escalation
    depends_on: [5.4]
    conditions:
      - if analyst_decision == "timeout":
          skip_to: 5.3  # Escalate to manager
      - if analyst_decision == "denied":
          skip_to: 9.2  # Log denial, end
        
  # ==================== LAYER 6: REMEDIATION ====================
  
  - id: 6.1
    name: verification_gate
    type: http_request
    mode: human_lead
    description: Verify with user before destructive action
    depends_on:
      - 5.4  # analyst approved
      - 5.5  # manager approved
    conditions:
      - if remediation_type IN ["disable_account", "isolate_device"]:
          action: verify_with_user
          timeout_minutes: 15
          timeout_action: proceed_anyway
          
  - id: 6.2
    name: execute_remediation
    type: http_request
    mode: deterministic
    description: Apply remediation via Graph API
    outputs:
      - remediation_result
      - before_state
      - after_state
    depends_on: [6.1]
    remediation_actions:
      disable_account:
        api_call:
          method: POST
          endpoint: "https://graph.microsoft.com/v1.0/users/${affected_user_id}/disable"
      reset_mfa:
        api_call:
          method: POST
          endpoint: "https://graph.microsoft.com/v1.0/users/${affected_user_id}/authentication/methods/reset"
      revoke_sessions:
        api_call:
          method: POST
          endpoint: "https://graph.microsoft.com/v1.0/users/${affected_user_id}/revokeSignInSessions"
          
  # ==================== LAYER 7: ORCHESTRATION ====================
  
  - id: 7.1
    name: create_itsm_ticket
    type: http_request
    mode: deterministic
    description: Create Jira/ServiceNow ticket
    outputs:
      - ticket_id
      - ticket_url
    depends_on: [6.2]
    api_call:
      method: POST
      endpoint: "${JIRA_API_URL}/issue"
      body:
        project: SECURITY
        issuetype: Incident
        summary: "M365: ${incident_type} - ${affected_user_id}"
        description: "{case_summary}"
        priority: "${assessed_severity}"
        
  - id: 7.2
    name: create_audit_record
    type: http_request
    mode: deterministic
    description: Create immutable compliance record
    depends_on:
      - 7.1
      - 6.2
    api_call:
      method: POST
      endpoint: "${TINES_API_URL}/records"
      body: >
        (See Section 7 Audit Record Schema)
        
  - id: 7.3
    name: update_case_timeline
    type: http_request
    mode: deterministic
    description: Add timeline events to case
    depends_on:
      - 7.2
      - 5.1  # Also runs on auto-response path
    api_call:
      method: POST
      endpoint: "${TINES_API_URL}/cases/${case_id}/events"
      body:
        event_type: incident_update
        timestamp: "${NOW}"
        details: "${outcome_summary}"
        
  - id: 7.4
    name: notify_stakeholders
    type: http_request
    mode: deterministic
    description: Send completion notifications
    depends_on: [7.3]
    conditions:
      - if assessed_severity == "Critical":
          notify: security_lead_email
      - if remediation_performed == true:
          notify: affected_user_email
          
  # ==================== LAYER 9: ERROR HANDLING ====================
  
  - id: 9.1
    name: log_duplicate
    type: http_request
    mode: deterministic
    description: Log duplicate alert and end
    depends_on: [1.3]
    when: is_duplicate == true
    
  - id: 9.2
    name: log_denial
    type: http_request
    mode: deterministic
    description: Log analyst denial, notify SOC
    depends_on: [5.5]
    when: analyst_decision == "denied"
    
  - id: 9.3
    name: dead_letter_handler
    type: http_request
    mode: deterministic
    description: Move failed alert to dead-letter queue
    depends_on: []
    when: any_action_fails
    resource: dead_letter_queue
    action: set
```

---

## 6. Branching Logic Summary

```
receive_webhook (1.1)
        ↓
validate_schema (1.2)
        ↓
check_deduplication (1.3)
        ↓
create_tines_case (1.4) ───────────────────────────────────────┐
        ↓                                                    │
log_to_deduplication_cache (1.5)                              │
        ↓                                                    │
get_graph_token (2.1)                                        │
        ↓                                                    │
┌───────┴───────┬───────┬───────┬───────┐                    │
↓               ↓       ↓       ↓       ↓                    │
enrich_user     enrich_  enrich_  enrich_  enrich_            │
profile (2.2)   signin  mail     device   group             │
                logs(2.3) activity(2.4) status(2.5) membership(2.6)
        ↓               ↓       ↓       ↓       ↓            │
        └───────────────┴───────┴───────┴───────┘            │
                         ↓                                   │
              aggregate_enrichment (2.7)                      │
                         ↓                                   │
        ┌────────────────┴────────────────┐                    │
        ↓                                 ↓                    │
generate_case_summary (3.1)              │                    │
        ↓                                 │                    │
classify_incident_type (3.2)             │                    │
        ↓                                 │                    │
assess_severity (3.3)                   │                    │
        ↓                                 │                    │
extract_iocs (3.4)                      │                    │
        ↓                                 │                    │
log_ai_interaction (3.5)                │                    │
        ↓                                 │                    │
    route_by_severity (4.1)──────────────┘                    │
        │                                                      │
        ├─ Low/Med + Conf>80% ─→ auto_response (5.1) ──────────→ 7.1
        │                                                              │
        ├─ High ─────────────────→ analyst_approval (5.2)            │
        │                              ↓                             │
        │                     wait_for_analyst (5.4)                  │
        │                              ↓                             │
        │                     escalation_handler (5.5)                  │
        │                              ↓                             │
        └─ Critical ──────────────→ critical_approval (5.3) ─────────→ 7.1
                                                                     │
                                                             verify_gate (6.1)
                                                                     ↓
                                                        execute_remediation (6.2)
                                                                     ↓
                                                            create_itsm (7.1)
                                                                     ↓
                                                            audit_record (7.2)
                                                                     ↓
                                                           update_timeline (7.3)
                                                                     ↓
                                                          notify_stakeholders (7.4)
```

---

## 7. Approval Gate Specifications

### Gate 1: Analyst Review (Step 5.2)

```yaml
approval_gate:
  id: analyst_review
  trigger: High severity OR (Medium + Low confidence)
  approver_role: security_analyst
  channel: slack_m365_incidents
  
  rich_notification:
    header: "🔔 Incident Review Required"
    severity_badge: "${assessed_severity}"
    summary: "${case_summary}"
    affected_user: "${affected_user_id}"
    iocs: "${iocs}"
    recommended_action: "${recommended_action}"
    
  action_buttons:
    - id: analyst_approve
      label: "✅ Approve"
      description: "Approve recommended action"
      
    - id: analyst_deny
      label: "❌ Deny"
      description: "Reject, mark as false positive"
      
    - id: analyst_more_info
      label: "ℹ️ More Info"
      description: "Request additional context"
      
  timeout:
    duration_minutes: 30
    action: escalate_to_manager
    
  escalation:
    next_gate: manager_approval
    notification: "⏰ Analyst review timed out, escalating to manager"
```

### Gate 2: Manager Approval (Step 5.3)

```yaml
approval_gate:
  id: manager_approval
  trigger: Critical severity OR analyst timeout
  approver_role: security_manager
  channel: slack_m365_security_leads
  
  rich_notification:
    header: "🚨 Critical Incident - Manager Approval Required"
    severity_badge: "CRITICAL"
    summary: "${case_summary}"
    blast_radius: "${risk_indicators}"
    recommended_action: "${recommended_action}"
    impact: "${business_impact}"
    
  action_buttons:
    - id: manager_approve
      label: "✅ Approve Containment"
      
    - id: manager_escalate
      label: "🚨 Escalate to CISO"
      
    - id: manager_deny
      label: "❌ Stand Down"
      
  timeout:
    duration_minutes: 15
    action: escalate_to_ciso
    
  escalation:
    next_gate: ciso_approval
```

### Gate 3: CISO Approval (Step 5.3 continued)

```yaml
approval_gate:
  id: ciso_approval
  trigger: Manager escalation
  approver_role: ciso
  channel: 
    - slack_m365_executive
    - pagerduty
  
  timeout:
    duration_minutes: 30
    action: auto_deny
    
  action_buttons:
    - id: ciso_full_approve
      label: "✅ Approve Full Response"
      
    - id: ciso_partial
      label: "⚠️ Partial Response"
      
    - id: ciso_stand_down
      label: "❌ Stand Down"
```

### Gate 4: User Verification (Step 6.1)

```yaml
verification_gate:
  id: user_verification
  trigger: Destructive action (disable, isolate)
  verify_with: affected_user
  channel: slack_direct_message
  
  message: |
    Security detected suspicious activity on your account.
    Did you authorize: ${suspicious_action}?
    
  action_buttons:
    - id: user_confirm
      label: "✅ Yes, I did this"
      
    - id: user_deny
      label: "❌ No, secure my account"
      
  timeout:
    duration_minutes: 15
    action: proceed_anyway  # Security override
    
  rationale: >
    User verification is advisory for critical incidents.
    Security takes precedence if user cannot be reached.
```

---

## 8. Error Handling Matrix

```yaml
error_handling:
  
  validation_errors:
    detection: schema_validation_fails
    action: reject_webhook
    response_code: 400
    log: severity=error
    
  deduplication_hits:
    detection: alert_id in cache
    action: skip_processing
    response_code: 200
    log: severity=info
    
  graph_api_rate_limit:
    detection: status_code == 429
    retry:
      max_attempts: 3
      backoff_seconds: [1, 2, 4]
    fallback: proceed_with_partial_enrichment
    alert: severity=warning
    
  graph_user_not_found:
    detection: status_code == 404
    action: continue_with_unknown_user
    flag: "user_enrichment_failed"
    
  ai_classification_failure:
    detection: llm_timeout OR llm_error
    fallback:
      use_rule_based_severity: "${original_severity}"
      confidence: 50
    alert: severity=warning
    
  approval_timeout:
    detection: timeout_elapsed
    action: escalate_to_next_approver
    log: severity=warning
    notify: approver_not_responded
    
  remediation_api_failure:
    detection: api_error
    retry:
      max_attempts: 3
      backoff_seconds: [2, 4, 8]
    fallback: flag_for_manual_review
    alert: severity=high
    dead_letter: true
    
  unknown_error:
    detection: any unhandled exception
    action: move_to_dead_letter
    alert: severity=high
```

---

## 9. Audit Record Schema

```json
{
  "record_type": "m365_incident_triage_audit",
  "spec_version": "1.0",
  "run_id": "uuid",
  "timestamp": "ISO8601",
  
  "trigger": {
    "source": "defender|sentinel|purview",
    "alert_id": "string",
    "received_at": "ISO8601",
    "payload_hash": "sha256"
  },
  
  "case": {
    "id": "string",
    "url": "string"
  },
  
  "enrichment": {
    "duration_ms": 1234,
    "graph_calls": [
      {"endpoint": "string", "status": "success|fail", "duration_ms": 123}
    ],
    "data_quality": "complete|partial|failed",
    "missing_fields": ["string"]
  },
  
  "classification": {
    "incident_type": "string",
    "severity": "string",
    "confidence": 0-100,
    "iocs": [
      {"type": "string", "value": "string"}
    ],
    "ai_model": "gpt-4"
  },
  
  "routing": {
    "path": "auto_response|analyst_review|critical_escalation",
    "decision_reason": "string"
  },
  
  "approval_chain": [
    {
      "gate": "analyst_review|manager_approval|ciso_approval|user_verification",
      "approver": "email or system",
      "decision": "approved|denied|escalated|timeout",
      "requested_at": "ISO8601",
      "decided_at": "ISO8601",
      "justification": "string (optional)"
    }
  ],
  
  "remediation": {
    "type": "string",
    "target": "string",
    "before_state": {},
    "after_state": {},
    "executed_at": "ISO8601",
    "success": true|false
  },
  
  "itsm": {
    "ticket_id": "string",
    "ticket_url": "string",
    "created_at": "ISO8601"
  },
  
  "ai_interactions": [
    {
      "action_id": "3.1|3.2|3.3|3.4",
      "prompt": "string (truncated to 1000 chars)",
      "response": "string (truncated to 1000 chars)",
      "tokens_used": 1234,
      "completed_at": "ISO8601"
    }
  ],
  
  "outcome": {
    "status": "resolved|escalated|failed",
    "resolution": "string",
    "duration_seconds": 1234,
    "completed_at": "ISO8601"
  }
}
```

---

## 10. Minimal v1 vs Expanded Production

### Minimal v1 Path (Quick Win)

For rapid deployment, implement only:

```yaml
minimal_v1_actions:
  - 1.1 receive_webhook
  - 1.2 validate_schema
  - 1.4 create_tines_case
  - 2.1 get_graph_token
  - 2.2 enrich_user_profile  # Just user profile, not all 5
  - 3.3 assess_severity      # Single AI call
  - 4.1 route_by_severity
  - 5.1 auto_response_notification  # Auto for all
  - 7.3 update_case_timeline
  
excluded_from_v1:
  - Deduplication (1.3, 1.5)
  - Parallel enrichment (2.2-2.6)
  - AI case summary (3.1)
  - Multi-step classification (3.2, 3.4)
  - AI interaction logging (3.5)
  - Human approval gates (5.2-5.5)
  - Verification gate (6.1)
  - Remediation (6.2)
  - ITSM integration (7.1)
  - Full audit record (7.2)
  
v1_limitations:
  - No duplicate detection
  - Single enrichment source
  - Single AI classification
  - No human oversight
  - Manual remediation required
  - Basic audit trail
```

### Expanded Production Path (Full Implementation)

All 25+ actions from Section 5, plus:

```yaml
production_additions:
  - Comprehensive deduplication
  - Full parallel enrichment
  - Multi-step AI classification
  - Three-tier approval gates
  - User verification gate
  - Automated remediation
  - ITSM integration
  - Complete audit compliance
  - Dead-letter queue handling
  - Alert filtering
  - Parallel sub-story calls
```

---

## 11. Assumptions & Gaps

### Assumptions

1. **Microsoft Graph API Access**
   - Assumed: Azure AD app registered with required permissions
   - Required permissions: User.Read, AuditLog.Read.All, Reports.Read.All, Directory.Read.All

2. **Tines Platform**
   - Assumed: Tines tenant with API access enabled
   - Required: API key with case/record creation permissions

3. **Notification Channel**
   - Assumed: Slack workspace with incoming webhook configured
   - Assumed: Dedicated #m365-incidents channel exists

4. **ITSM Integration**
   - Assumed: Jira or ServiceNow instance accessible
   - Required: API token with issue creation permissions

5. **AI Model**
   - Assumed: OpenAI API access or Tines AI integration
   - Model: GPT-4 or equivalent

6. **Alert Source**
   - Assumed: Microsoft Defender or Sentinel forwarding alerts
   - Assumed: Webhook authentication configured

### Gaps to Resolve Before Implementation

| Gap | Priority | Owner |
|-----|----------|-------|
| Azure AD app client ID/secret | HIGH | Security Ops |
| Tines API key | HIGH | Tines Admin |
| Folder ID for cases | HIGH | Tines Admin |
| Slack webhook URL | MEDIUM | Slack Admin |
| Jira API token + URL | MEDIUM | Jira Admin |
| On-call schedule integration | MEDIUM | Security Ops |
| Verification Slack DM capability | MEDIUM | Slack Admin |
| PagerDuty integration for CISO | LOW | On-call vendor |

### Placeholders to Replace

```bash
# In this spec, replace these placeholders:
${MS_GRAPH_CLIENT_ID}     # Azure AD app registration
${MS_GRAPH_CLIENT_SECRET}  # Azure AD app registration
${MS_GRAPH_TENANT_ID}     # Azure AD tenant
${TINES_API_KEY}          # Tines platform
${TINES_API_URL}          # Usually: https://your-tenant.tines.com/api/v1
${FOLDER_ID}             # Tines folder for cases
${TEAM_ID}               # Tines team
${SLACK_WEBHOOK_URL}      # Slack incoming webhook
${JIRA_API_TOKEN}        # Jira API token
${JIRA_API_URL}           # Jira instance URL
${TINES_API_URL}         # Tines API base URL
```

---

## 12. Implementation Notes

### Parallel Enrichment Pattern

The Graph enrichment calls (2.2-2.6) are marked with `parallel_group: graph_enrichment`. In Tines:
1. Create these as parallel branches in Storyboard
2. Add a "wait" action that depends on all parallel branches
3. Aggregate results in the wait action

### Approval State Tracking

The `approval_states` resource tracks:
```json
{
  "approval_request_id": "uuid",
  "status": "pending|approved|denied|timeout",
  "approver_email": "string",
  "created_at": "ISO8601",
  "expires_at": "ISO8601"
}
```

Use a scheduled story or Tines Timer to check expired approvals.

### Sub-Story Extraction Points

These could become standalone reusable stories:
1. `m365-graph-enrichment` - Steps 2.1-2.7
2. `m365-severity-classifier` - Steps 3.1-3.4
3. `approval-gate` - Steps 5.2-5.5
4. `audit-record` - Step 7.2

---

## 13. Review Checklist

Before creating the Tines story:

- [ ] All placeholders replaced with actual values
- [ ] Azure AD app registered with required permissions
- [ ] Tines credentials configured and tested
- [ ] Slack channel and webhook created
- [ ] Jira/ServiceNow configured
- [ ] AI model access verified
- [ ] Webhook endpoint registered with Defender/Sentinel
- [ ] On-call schedule mapped to approvers
- [ ] Audit requirements confirmed (SOC2, ISO27001, etc.)
- [ ] Stakeholder sign-off obtained

---

*This specification maps directly to `M365_INCIDENT_TRIAGE_BLUEPRINT.md`. All 25 actions from the blueprint are represented with technical implementation details for Tines.*
