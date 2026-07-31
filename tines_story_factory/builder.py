"""Builder Agent for Tines Story Factory.

Generates the complete Tines story specification including:
- Story JSON structure
- Action configurations
- Credential requirements
- Trigger setup
"""
from .base import TinesBaseAgent, TinesAgentState


class TinesBuilderAgent(TinesBaseAgent):
    """Builder agent that generates Tines story specifications."""
    
    def __init__(self):
        super().__init__(
            name="TinesBuilder",
            description="Generates Tines story specifications"
        )
    
    async def process(self, state: TinesAgentState) -> dict:
        """Build the Tines story specification."""
        self._log(f"Building story specification with {len(state.action_specs)} actions")
        
        # Build story specification
        story_spec = self._build_story_spec(
            state.story_architecture,
            state.action_specs,
            state.data_flow
        )
        
        # Build actions JSON
        actions_json = self._build_actions_json(state.action_specs)
        
        # Identify required credentials
        credentials_needed = self._identify_credentials(state.action_specs)
        
        self._log(f"Generated spec with {len(actions_json)} actions")
        
        return {
            "story_spec": story_spec,
            "actions_json": actions_json,
            "credentials_needed": credentials_needed,
            "agent_results": {
                **state.agent_results,
                "builder": {
                    "actions_generated": len(actions_json),
                    "credentials_needed": len(credentials_needed),
                    "status": "completed"
                }
            }
        }
    
    def _build_story_spec(self, architecture: dict, actions: list, data_flow: dict) -> dict:
        """Build the complete story specification."""
        return {
            "name": architecture.get("name", "Tines Workflow"),
            "description": architecture.get("description", ""),
            "workflow_type": architecture.get("workflow_type", ""),
            "layers": architecture.get("layers", []),
            "complexity": architecture.get("complexity", "medium"),
            "approval_gates": architecture.get("approval_gates", 0),
            "version": "1.0.0",
            "actions": [a["name"] for a in actions],
            "data_flow": data_flow,
            "metadata": {
                "generated_by": "LangGraph Tines Story Factory",
                "agent_version": "1.0.0"
            }
        }
    
    def _build_actions_json(self, action_specs: list) -> list:
        """Build JSON representation of actions."""
        actions_json = []
        
        for spec in action_specs:
            action = self._build_action_json(spec)
            actions_json.append(action)
        
        return actions_json
    
    def _build_action_json(self, spec: dict) -> dict:
        """Build JSON for a single action."""
        action_type = spec.get("type", "WebhookAgent")
        
        base_action = {
            "name": spec.get("name", ""),
            "type": action_type,
            "layer": spec.get("layer", ""),
            "purpose": spec.get("purpose", ""),
            "mode": spec.get("mode", "D"),  # D=Deterministic, A=Agentic, H=Human
            "config": spec.get("config", {})
        }
        
        # Add approval gate info if present
        if spec.get("approval_gate"):
            base_action["approval"] = {
                "required": True,
                "timeout_minutes": spec.get("timeout", 30),
                "approver": self._get_approver(spec)
            }
        
        # Type-specific configurations
        if action_type == "WebhookAgent":
            base_action["webhook"] = {
                "receive": True,
                "path": f"/webhook/{spec.get('name', 'default')}"
            }
        
        elif action_type == "MicrosoftGraphAgent":
            base_action["microsoft_graph"] = {
                "scope": "https://graph.microsoft.com/.default"
            }
        
        elif action_type == "OpenAIAgent":
            base_action["openai"] = {
                "model": "gpt-4",
                "temperature": 0.3
            }
        
        elif action_type == "EmailAgent":
            base_action["email"] = {
                "provider": "smtp",
                "from": "noreply@company.com"
            }
        
        elif action_type == "SlackAgent":
            base_action["slack"] = {
                "workspace": "company"
            }
        
        elif action_type == "JiraAgent":
            base_action["jira"] = {
                "site": "company.atlassian.net"
            }
        
        return base_action
    
    def _get_approver(self, spec: dict) -> str:
        """Determine approver based on action type."""
        name = spec.get("name", "").lower()
        
        if "analyst" in name:
            return "security_analyst"
        elif "manager" in name:
            return "security_manager"
        elif "ciso" in name:
            return "ciso"
        elif "block" in name or "disable" in name:
            return "security_manager"
        
        return "security_analyst"
    
    def _identify_credentials(self, action_specs: list) -> list:
        """Identify required credentials."""
        credentials = set()
        
        for spec in action_specs:
            action_type = spec.get("type", "")
            
            if action_type == "MicrosoftGraphAgent":
                credentials.add("microsoft_graph_client_id")
                credentials.add("microsoft_graph_client_secret")
                credentials.add("microsoft_graph_tenant_id")
            
            elif action_type == "OpenAIAgent":
                credentials.add("openai_api_key")
            
            elif action_type == "SlackAgent":
                credentials.add("slack_webhook_url")
            
            elif action_type == "JiraAgent":
                credentials.add("jira_api_token")
                credentials.add("jira_domain")
            
            elif action_type == "EmailAgent":
                credentials.add("smtp_username")
                credentials.add("smtp_password")
        
        return sorted(list(credentials))
