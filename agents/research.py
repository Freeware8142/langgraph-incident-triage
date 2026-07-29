"""Research agent for gathering incident context."""
import httpx
from .base import BaseAgent, AgentState


class ResearchAgent(BaseAgent):
    """Collects relevant data from Microsoft Graph and external sources."""

    def __init__(self):
        super().__init__(
            name="research",
            description="Gathers context data for incident triage"
        )

    async def process(self, state: AgentState) -> AgentState:
        """Research the incident and collect relevant data."""
        incident_id = state["incident_id"]
        incident_data = state.get("incident_data", {})

        research_data = {
            "incident_id": incident_id,
            "severity_indicators": self._analyze_severity(incident_data),
            "affected_services": self._get_affected_services(incident_data),
            "historical_context": await self._fetch_historical_data(incident_id),
            "related_incidents": await self._find_related_incidents(incident_data),
        }

        return {**state, "research_data": research_data}

    def _analyze_severity(self, incident_data: dict) -> dict:
        """Analyze severity indicators from incident data."""
        return {
            "impact_score": incident_data.get("impactScore", "unknown"),
            "priority": incident_data.get("priority", "unknown"),
            "user_impact": incident_data.get("userImpact", "unknown"),
        }

    def _get_affected_services(self, incident_data: dict) -> list[str]:
        """Extract affected services from incident data."""
        return incident_data.get("affectedServices", [])

    async def _fetch_historical_data(self, incident_id: str) -> dict:
        """Fetch historical data for similar incidents."""
        # Microsoft Graph API integration
        return {"similar_incidents": [], "resolution_patterns": []}

    async def _find_related_incidents(self, incident_data: dict) -> list[dict]:
        """Find related incidents using Tines API."""
        # Tines API integration
        return []
