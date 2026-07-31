"""Architect Agent for Tines Story Factory.

Designs the Tines story architecture including:
- Action list and their purposes
- Data flow between actions
- Approval gates
- Error handling
"""
from .base import TinesBaseAgent, TinesAgentState


class TinesArchitectAgent(TinesBaseAgent):
    """Architect agent that designs Tines story workflows."""
    
    def __init__(self):
        super().__init__(
            name="TinesArchitect", 
            description="Designs Tines story architecture"
        )
    
    async def process(self, state: TinesAgentState) -> dict:
        """Design the Tines story architecture."""
        self._log(f"Designing architecture for: {state.story_requirements}")
        
        # Determine story architecture based on requirements
        architecture = self._design_architecture(
            state.story_requirements,
            state.workflow_type,
            state.existing_patterns
        )
        
        # Design action specifications
        action_specs = self._design_actions(
            architecture,
            state.story_requirements,
            state.best_practices
        )
        
        # Design data flow
        data_flow = self._design_data_flow(action_specs)
        
        self._log(f"Designed {len(action_specs)} actions")
        
        return {
            "story_architecture": architecture,
            "action_specs": action_specs,
            "data_flow": data_flow,
            "agent_results": {
                **state.agent_results,
                "architect": {
                    "actions_designed": len(action_specs),
                    "approval_gates": architecture.get("approval_gates", 0),
                    "status": "completed"
                }
            }
        }
    
    def _design_architecture(self, requirements: str, workflow_type: str, patterns: list) -> dict:
        """Design the overall story architecture."""
        architecture = {
            "name": self._extract_name(requirements),
            "description": self._extract_description(requirements),
            "workflow_type": workflow_type,
            "layers": [],
            "approval_gates": 0,
            "complexity": "medium"
        }
        
        # Design based on workflow type
        if workflow_type in ["incident_triage", "security", "m365"]:
            architecture["layers"] = [
                {"name": "Ingestion", "purpose": "Receive and normalize alerts"},
                {"name": "Enrichment", "purpose": "Gather additional context"},
                {"name": "Classification", "purpose": "Determine severity and type"},
                {"name": "Routing", "purpose": "Route to appropriate response path"},
                {"name": "Response", "purpose": "Execute response actions"},
                {"name": "Orchestration", "purpose": "Coordinate with external systems"}
            ]
            architecture["approval_gates"] = 4
        
        return architecture
    
    def _design_actions(self, architecture: dict, requirements: str, best_practices: list) -> list:
        """Design individual actions for the story."""
        actions = []
        action_id = 1
        
        workflow_type = architecture.get("workflow_type", "")
        
        if workflow_type in ["incident_triage", "security", "m365"]:
            # Layer 1: Ingestion
            actions.extend([
                {
                    "id": action_id,
                    "name": "receive_webhook",
                    "type": "WebhookAgent",
                    "layer": "Ingestion",
                    "purpose": "Receive alerts from Defender/Sentinel",
                    "config": {"name": "m365_security_alerts"},
                    "mode": "D"
                },
                {
                    "id": action_id + 1,
                    "name": "parse_alert",
                    "type": "JSONPathAgent",
                    "layer": "Ingestion",
                    "purpose": "Extract key fields from alert",
                    "config": {"expression": "$.alert.*"},
                    "mode": "D"
                },
            ])
            action_id += 2
            
            # Layer 2: Enrichment
            actions.extend([
                {
                    "id": action_id,
                    "name": "get_user_info",
                    "type": "MicrosoftGraphAgent",
                    "layer": "Enrichment",
                    "purpose": "Get user details from Azure AD",
                    "config": {"endpoint": "/users/{user_id}"},
                    "mode": "D"
                },
                {
                    "id": action_id + 1,
                    "name": "check_signin_logs",
                    "type": "MicrosoftGraphAgent",
                    "layer": "Enrichment",
                    "purpose": "Check recent sign-in activity",
                    "config": {"endpoint": "/auditLogs/signIns"},
                    "mode": "D"
                },
            ])
            action_id += 2
            
            # Layer 3: Classification
            actions.extend([
                {
                    "id": action_id,
                    "name": "classify_incident",
                    "type": "OpenAIAgent",
                    "layer": "Classification",
                    "purpose": "AI-powered incident classification",
                    "config": {"prompt": "Classify incident severity and type"},
                    "mode": "A"
                },
                {
                    "id": action_id + 1,
                    "name": "determine_severity",
                    "type": "ConditionalAgent",
                    "layer": "Classification",
                    "purpose": "Route based on severity",
                    "config": {"field": "severity", "values": ["critical", "high", "medium", "low"]},
                    "mode": "D"
                }
            ])
            action_id += 2
            
            # Layer 4: Routing with Approval
            actions.extend([
                {
                    "id": action_id,
                    "name": "analyst_approval",
                    "type": "EmailAgent",
                    "layer": "Routing",
                    "purpose": "Request analyst approval for high severity",
                    "config": {"to": "analyst@company.com", "template": "approval_request"},
                    "mode": "H",
                    "approval_gate": True,
                    "timeout": 30
                },
                {
                    "id": action_id + 1,
                    "name": "route_to_response",
                    "type": "ConditionalAgent",
                    "layer": "Routing",
                    "purpose": "Route to appropriate response path",
                    "config": {"based_on": "severity"},
                    "mode": "D"
                }
            ])
            action_id += 2
            
            # Layer 5: Response
            actions.extend([
                {
                    "id": action_id,
                    "name": "block_user",
                    "type": "MicrosoftGraphAgent",
                    "layer": "Response",
                    "purpose": "Block compromised user account",
                    "config": {"action": "disable"},
                    "mode": "H",
                    "approval_gate": True,
                    "timeout": 15
                },
                {
                    "id": action_id + 1,
                    "name": "revoke_sessions",
                    "type": "MicrosoftGraphAgent",
                    "layer": "Response",
                    "purpose": "Revoke active user sessions",
                    "config": {"action": "signOut"},
                    "mode": "D"
                }
            ])
            action_id += 2
            
            # Layer 6: Orchestration
            actions.extend([
                {
                    "id": action_id,
                    "name": "create_jira_ticket",
                    "type": "JiraAgent",
                    "layer": "Orchestration",
                    "purpose": "Create incident ticket in Jira",
                    "config": {"project": "SEC", "type": "Incident"},
                    "mode": "D"
                },
                {
                    "id": action_id + 1,
                    "name": "notify_slack",
                    "type": "SlackAgent",
                    "layer": "Orchestration",
                    "purpose": "Notify security team in Slack",
                    "config": {"channel": "#security-alerts"},
                    "mode": "D"
                },
                {
                    "id": action_id + 2,
                    "name": "close_incident",
                    "type": "TemplateAgent",
                    "layer": "Orchestration",
                    "purpose": "Generate incident summary",
                    "config": {"template": "incident_closed"},
                    "mode": "D"
                }
            ])
        
        return actions
    
    def _design_data_flow(self, actions: list) -> dict:
        """Design the data flow between actions."""
        data_flow = {}
        
        for i, action in enumerate(actions):
            action_name = action["name"]
            data_flow[action_name] = {
                "inputs": [],
                "outputs": [],
                "next": []
            }
            
            # Define inputs from previous action outputs
            if i > 0:
                prev_action = actions[i - 1]
                data_flow[action_name]["inputs"].append({
                    "from": prev_action["name"],
                    "field": "result"
                })
            
            # Define next actions
            if i < len(actions) - 1:
                data_flow[action_name]["next"].append(actions[i + 1]["name"])
        
        return data_flow
    
    def _extract_name(self, requirements: str) -> str:
        """Extract story name from requirements."""
        # Simple extraction - can be enhanced with LLM
        if "m365" in requirements.lower() or "microsoft" in requirements.lower():
            return "M365 Security Incident Triage"
        return "Tines Workflow"
    
    def _extract_description(self, requirements: str) -> str:
        """Extract description from requirements."""
        return requirements[:200] if requirements else "Automated workflow"
