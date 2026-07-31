"""Research Agent for Tines Story Factory.

Researches Tines API capabilities, existing stories, and patterns
to inform the story architecture and design.
"""
from .base import TinesBaseAgent, TinesAgentState


class TinesResearchAgent(TinesBaseAgent):
    """Research agent that investigates Tines capabilities and patterns."""
    
    def __init__(self):
        super().__init__(
            name="TinesResearch",
            description="Researches Tines API and best practices"
        )
    
    async def process(self, state: TinesAgentState) -> dict:
        """Research Tines API capabilities and existing patterns."""
        self._log(f"Researching for workflow type: {state.workflow_type}")
        
        # Research Tines API capabilities
        api_capabilities = await self._research_api_capabilities()
        
        # Research existing patterns
        patterns = await self._research_patterns(state.workflow_type)
        
        # Research best practices
        best_practices = await self._research_best_practices(state.workflow_type)
        
        self._log(f"Found {len(patterns)} relevant patterns")
        
        return {
            "tines_api_capabilities": api_capabilities,
            "existing_patterns": patterns,
            "best_practices": best_practices,
            "agent_results": {
                **state.agent_results,
                "research": {
                    "patterns_found": len(patterns),
                    "api_version": "v1",
                    "status": "completed"
                }
            }
        }
    
    async def _research_api_capabilities(self) -> dict:
        """Research Tines API capabilities."""
        return {
            "api_version": "v1",
            "story_management": {
                "create": True,
                "update": True,
                "delete": True,
                "list": True,
                "clone": True
            },
            "action_types": [
                "WebhookAgent",
                "HTTPAgent", 
                "EmailAgent",
                "SlackAgent",
                "ConditionalAgent",
                "DelayAgent",
                "JSONPathAgent",
                "Base64Agent",
                "TemplateAgent",
                "LoopAgent",
                "OCRDocumentAgent",
                "PDFDocumentAgent",
                "GoogleSheetsAgent",
                "CalendarAgent",
                "GitHubAgent",
                "JiraAgent",
                "ServiceNowAgent",
                "SplunkAgent",
                "MicrosoftGraphAgent",
                "OpenAIAgent",
                "AnthropicAgent"
            ],
            "authentication_types": [
                "api_key",
                "oauth2", 
                "basic_auth",
                "certificate"
            ],
            "trigger_types": [
                "webhook",
                "schedule",
                "email",
                "manual"
            ],
            "webhook_features": {
                "receive_webhook": True,
                "send_webhook": True,
                "custom_headers": True,
                "hmac_validation": True
            }
        }
    
    async def _research_patterns(self, workflow_type: str) -> list:
        """Research existing Tines workflow patterns."""
        patterns = []
        
        # Common workflow patterns
        if workflow_type in ["incident_triage", "security", "m365"]:
            patterns.extend([
                {
                    "name": "Multi-Tool IOC Enrichment",
                    "description": "Enrich indicators with multiple threat intel tools",
                    "actions": ["LoopAgent", "HTTPAgent", "JSONPathAgent"],
                    "complexity": "medium",
                    "applicable": True
                },
                {
                    "name": "Approval Gate with Escalation",
                    "description": "Human approval with timeout escalation",
                    "actions": ["ConditionalAgent", "EmailAgent", "DelayAgent"],
                    "complexity": "medium",
                    "applicable": True
                },
                {
                    "name": "Parallel Enrichment",
                    "description": "Enrich multiple IOCs simultaneously",
                    "actions": ["LoopAgent"],
                    "complexity": "low",
                    "applicable": True
                },
                {
                    "name": "Destructive Action Safety",
                    "description": "Verify destructive actions with human approval",
                    "actions": ["ConditionalAgent", "WebhookAgent"],
                    "complexity": "high",
                    "applicable": True
                }
            ])
        
        if workflow_type == "m365" or "microsoft" in workflow_type.lower():
            patterns.append({
                "name": "Microsoft Graph Integration",
                "description": "Use Microsoft Graph for M365 data",
                "actions": ["MicrosoftGraphAgent"],
                "complexity": "medium",
                "applicable": True
            })
        
        return patterns
    
    async def _research_best_practices(self, workflow_type: str) -> list:
        """Research Tines best practices."""
        return [
            {
                "category": "Design",
                "practice": "Use descriptive action names",
                "rationale": "Makes debugging and maintenance easier"
            },
            {
                "category": "Design", 
                "practice": "Keep actions single-purpose",
                "rationale": "Improves reusability and testability"
            },
            {
                "category": "Security",
                "practice": "Store credentials in Tines vault",
                "rationale": "Secure storage, easy rotation"
            },
            {
                "category": "Security",
                "practice": "Add approval gates for destructive actions",
                "rationale": "Prevent accidental data loss"
            },
            {
                "category": "Performance",
                "practice": "Use parallel execution where possible",
                "rationale": "Reduce workflow execution time"
            },
            {
                "category": "Monitoring",
                "practice": "Set up error monitoring",
                "rationale": "Catch failures before users report them"
            },
            {
                "category": "Documentation",
                "practice": "Document story purpose and data flow",
                "rationale": "Onboarding and troubleshooting"
            }
        ]
