"""Documenter Agent for Tines Story Factory.

Generates documentation for the Tines story:
- Story overview
- Action descriptions
- Data flow diagrams
- Deployment guide
- Credential setup
"""
from .base import TinesBaseAgent, TinesAgentState


class TinesDocumenterAgent(TinesBaseAgent):
    """Documenter agent that generates Tines story documentation."""
    
    def __init__(self):
        super().__init__(
            name="TinesDocumenter",
            description="Documents Tines story specifications"
        )
    
    async def process(self, state: TinesAgentState) -> dict:
        """Generate documentation for the story."""
        self._log("Generating documentation")
        
        # Generate main documentation
        documentation = self._generate_documentation(state)
        
        # Generate deployment guide
        deployment_guide = self._generate_deployment_guide(state)
        
        self._log("Documentation generated")
        
        return {
            "documentation": documentation,
            "deployment_guide": deployment_guide,
            "agent_results": {
                **state.agent_results,
                "documenter": {
                    "sections_generated": 5,
                    "status": "completed"
                }
            }
        }
    
    def _generate_documentation(self, state: TinesAgentState) -> str:
        """Generate comprehensive documentation."""
        
        doc = f"""# {state.story_spec.get('name', 'Tines Story')}

{state.story_spec.get('description', '')}

## Overview

| Property | Value |
|----------|-------|
| **Workflow Type** | {state.story_spec.get('workflow_type', 'N/A')} |
| **Complexity** | {state.story_spec.get('complexity', 'Medium')} |
| **Actions** | {len(state.actions_json)} |
| **Approval Gates** | {state.story_spec.get('approval_gates', 0)} |
| **Generated** | By LangGraph Tines Story Factory |

## Architecture

### Layers

"""
        
        # Document layers
        layers = state.story_spec.get('layers', [])
        for layer in layers:
            doc += f"""#### {layer.get('name', 'Unknown')}
**Purpose:** {layer.get('purpose', 'N/A')}

"""
        
        # Document actions
        doc += """## Actions

"""
        
        actions_by_layer = {}
        for action in state.actions_json:
            layer = action.get("layer", "Other")
            if layer not in actions_by_layer:
                actions_by_layer[layer] = []
            actions_by_layer[layer].append(action)
        
        for layer, actions in actions_by_layer.items():
            doc += f"""### {layer}

"""
            for action in actions:
                mode_icon = {"D": "⚙️", "A": "🤖", "H": "👤"}.get(action.get("mode", "D"), "⚙️")
                approval_text = " **[APPROVAL REQUIRED]**" if action.get("approval", {}).get("required") else ""
                
                doc += f"""#### {action.get('name', 'Unnamed')} {mode_icon}{approval_text}
- **Type:** {action.get('type', 'Unknown')}
- **Purpose:** {action.get('purpose', 'N/A')}

"""
        
        # Document credentials
        doc += """## Required Credentials

"""
        
        for cred in state.credentials_needed:
            doc += f"- `{cred}`\n"
        
        doc += "\n## Data Flow\n\n"
        
        # Document data flow
        data_flow = state.data_flow
        if data_flow:
            doc += "```\n"
            for action_name, flow in data_flow.items():
                next_actions = ", ".join(flow.get("next", [])) or "END"
                doc += f"{action_name} → {next_actions}\n"
            doc += "```\n"
        
        return doc
    
    def _generate_deployment_guide(self, state: TinesAgentState) -> str:
        """Generate deployment guide."""
        
        guide = """# Deployment Guide

## Prerequisites

1. Tines account with API access
2. Required credentials configured in Tines vault
3. Appropriate team permissions

## Setup Steps

### 1. Configure Credentials

In Tines, go to **Credentials** and add the following:

"""
        
        for cred in state.credentials_needed:
            guide += f"""#### {cred}
- **Type:** Text / Secret
- **Description:** Required for story execution

"""
        
        guide += """### 2. Create the Story

1. Log into Tines
2. Create a new story or import from specification
3. Add actions as defined in the specification
4. Configure triggers

### 3. Configure Webhook (if applicable)

"""
        
        # Check for webhook triggers
        webhook_actions = [a for a in state.actions_json if a.get("webhook", {}).get("receive")]
        if webhook_actions:
            guide += "The following endpoints receive webhooks:\n\n"
            for action in webhook_actions:
                path = action.get("webhook", {}).get("path", "/webhook")
                guide += f"- `{path}` → {action.get('name')}\n"
        else:
            guide += "No webhook triggers configured.\n"
        
        guide += """
### 4. Test the Story

1. Enable the story in **DRAFT** mode
2. Send a test event
3. Monitor execution in **Events**
4. Verify all actions execute correctly
5. Enable **LIVE** mode when ready

### 5. Monitoring

- Set up email alerts for failures
- Monitor event history regularly
- Review approval queue for pending actions

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Story not triggering | Check webhook URL and credentials |
| Action failing | Verify credential permissions |
| Approval not received | Check email settings |

"""
        
        return guide
