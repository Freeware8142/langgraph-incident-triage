"""Base agent for Tines Story Factory."""
from abc import ABC, abstractmethod
from typing import Any
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field


class TinesAgentState(BaseModel):
    """State passed between agents in the Tines Story Factory."""
    # Input
    story_requirements: str = Field(default="", description="User's story requirements")
    workflow_type: str = Field(default="", description="Type of workflow to create")
    
    # Research outputs
    tines_api_capabilities: dict = Field(default_factory=dict, description="Tines API capabilities")
    existing_patterns: list = Field(default_factory=list, description="Existing Tines patterns")
    best_practices: list = Field(default_factory=list, description="Tines best practices")
    
    # Architect outputs
    story_architecture: dict = Field(default_factory=dict, description="Story architecture design")
    action_specs: list = Field(default_factory=list, description="List of actions to create")
    data_flow: dict = Field(default_factory=dict, description="Data flow between actions")
    
    # Builder outputs
    story_spec: dict = Field(default_factory=dict, description="Complete story specification")
    actions_json: list = Field(default_factory=list, description="Actions in JSON format")
    credentials_needed: list = Field(default_factory=list, description="Required credentials")
    
    # Tester outputs
    validation_results: dict = Field(default_factory=dict, description="Validation results")
    issues_found: list = Field(default_factory=list, description="Issues found during testing")
    recommendations: list = Field(default_factory=list, description="Recommendations for improvement")
    
    # Documenter outputs
    documentation: str = Field(default="", description="Generated documentation")
    deployment_guide: str = Field(default="", description="Deployment instructions")
    
    # Metadata
    error: str | None = Field(default=None, description="Error message if any")
    agent_results: dict = Field(default_factory=dict, description="Results from each agent")


class TinesBaseAgent(ABC):
    """Base class for Tines Story Factory agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, state: TinesAgentState) -> dict:
        """Process the state and return updates."""
        pass
    
    def _create_node(self):
        """Create a LangGraph node from this agent."""
        async def node(state: TinesAgentState) -> dict:
            return await self.process(state)
        return node
    
    def _log(self, message: str):
        """Log agent activity."""
        print(f"[{self.name}] {message}")
