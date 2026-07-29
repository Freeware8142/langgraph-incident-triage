"""Base agent interface for the incident triage system."""
from abc import ABC, abstractmethod
from typing import Any, TypedDict


class AgentState(TypedDict):
    """Shared state between agents."""
    incident_id: str
    incident_data: dict
    triage_result: dict | None
    research_data: dict | None
    analysis: str | None
    recommendation: str | None
    build_output: str | None
    test_results: dict | None
    documentation: str | None
    error: str | None


class BaseAgent(ABC):
    """Base class for all agents in the triage system."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Process the incident and update state."""
        pass

    def _create_node(self):
        """Create a LangGraph node function for this agent."""
        async def node(state: AgentState) -> AgentState:
            try:
                return await self.process(state)
            except Exception as e:
                return {**state, "error": str(e)}
        return node
