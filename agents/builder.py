"""Builder agent for generating remediation scripts."""
from .base import BaseAgent, AgentState


class BuilderAgent(BaseAgent):
    """Generates automated remediation scripts and runbooks."""

    def __init__(self):
        super().__init__(
            name="builder",
            description="Generates remediation scripts and automation"
        )

    async def process(self, state: AgentState) -> AgentState:
        """Build remediation automation based on analysis."""
        analysis = state.get("analysis", "")
        incident_data = state.get("incident_data", {})
        recommendation = state.get("recommendation", "")

        build_output = self._generate_remediation(incident_data, recommendation)

        return {**state, "build_output": build_output}

    def _generate_remediation(
        self, incident_data: dict, recommendation: str
    ) -> str:
        """Generate remediation script based on incident type."""
        incident_type = incident_data.get("type", "generic")

        scripts = {
            "network": self._network_remediation(),
            "database": self._database_remediation(),
            "auth": self._auth_remediation(),
            "compute": self._compute_remediation(),
        }

        script = scripts.get(
            incident_type,
            self._generic_remediation()
        )

        return f"""# Auto-generated Remediation Script
# Incident Type: {incident_type}
# Generated at: {self._timestamp()}

{recommendation}

{script}
"""

    def _network_remediation(self) -> str:
        return '''#!/bin/bash
# Network Remediation Steps
set -e

echo "Checking network connectivity..."
# Add network diagnostic steps here
# curl -I https://health.internal
# Check DNS resolution
# Verify load balancer health

echo "Network remediation complete"
'''

    def _database_remediation(self) -> str:
        return '''#!/bash
# Database Remediation Steps
set -e

echo "Checking database connections..."
# Add database diagnostic steps here
# Verify connection pools
# Check replication lag
# Analyze slow queries

echo "Database remediation complete"
'''

    def _auth_remediation(self) -> str:
        return '''#!/bin/bash
# Authentication Remediation Steps
set -e

echo "Checking authentication systems..."
# Add auth diagnostic steps here
# Verify token service
# Check Azure AD connectivity
# Review failed login attempts

echo "Authentication remediation complete"
'''

    def _compute_remediation(self) -> str:
        return '''#!/bin/bash
# Compute Remediation Steps
set -e

echo "Checking compute resources..."
# Add compute diagnostic steps here
# Check instance health
# Verify auto-scaling
# Review resource utilization

echo "Compute remediation complete"
'''

    def _generic_remediation(self) -> str:
        return '''#!/bin/bash
# Generic Remediation Steps
set -e

echo "Running generic diagnostics..."
# Add generic diagnostic steps here

echo "Generic remediation complete"
'''

    def _timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()
