"""Architect agent for analyzing incident patterns."""
from .base import BaseAgent, AgentState


class ArchitectAgent(BaseAgent):
    """Analyzes incident patterns and determines resolution strategy."""

    def __init__(self):
        super().__init__(
            name="architect",
            description="Analyzes incident patterns and designs resolution"
        )

    async def process(self, state: AgentState) -> AgentState:
        """Analyze the incident and create a resolution plan."""
        research_data = state.get("research_data", {})
        incident_data = state.get("incident_data", {})

        analysis = self._perform_root_cause_analysis(
            research_data, incident_data
        )

        recommendation = self._generate_recommendation(
            analysis, research_data
        )

        return {
            **state,
            "analysis": analysis,
            "recommendation": recommendation,
        }

    def _perform_root_cause_analysis(
        self, research_data: dict, incident_data: dict
    ) -> str:
        """Perform root cause analysis on the incident."""
        severity = research_data.get("severity_indicators", {})
        affected = research_data.get("affected_services", [])

        if severity.get("priority") == "critical" or severity.get("impact_score") == "high":
            return (
                "Critical incident detected. Likely root cause: "
                f"Service degradation in {', '.join(affected) if affected else 'unknown systems'}. "
                "Immediate escalation recommended."
            )

        return (
            f"Analysis of {len(affected)} affected services. "
            "Pattern suggests configuration or dependency issue."
        )

    def _generate_recommendation(
        self, analysis: str, research_data: dict
    ) -> str:
        """Generate actionable recommendation based on analysis."""
        return f"""
Recommended Actions:
1. Immediate: Review recent deployments in affected services
2. Short-term: Enable enhanced monitoring for affected systems
3. Long-term: Implement preventive measures based on historical patterns
"""
