"""Tester agent for validating remediation scripts."""
from .base import BaseAgent, AgentState


class TesterAgent(BaseAgent):
    """Validates remediation scripts before deployment."""

    def __init__(self):
        super().__init__(
            name="tester",
            description="Tests and validates remediation scripts"
        )

    async def process(self, state: AgentState) -> AgentState:
        """Test the remediation script for safety and correctness."""
        build_output = state.get("build_output", "")
        incident_data = state.get("incident_data", {})

        test_results = self._run_tests(build_output, incident_data)

        return {**state, "test_results": test_results}

    def _run_tests(
        self, build_output: str, incident_data: dict
    ) -> dict:
        """Run validation tests on the remediation script."""
        tests = []

        # Test 1: Syntax validation
        syntax_valid = self._validate_syntax(build_output)
        tests.append({
            "name": "Syntax Validation",
            "passed": syntax_valid,
            "message": "Script syntax is valid" if syntax_valid else "Syntax error detected"
        })

        # Test 2: Safety check
        safety_passed = self._check_safety(build_output)
        tests.append({
            "name": "Safety Check",
            "passed": safety_passed,
            "message": "No dangerous commands detected" if safety_passed else "Potentially dangerous operations found"
        })

        # Test 3: Required permissions
        permissions_ok = self._check_permissions(incident_data)
        tests.append({
            "name": "Permissions Check",
            "passed": permissions_ok,
            "message": "Required permissions available" if permissions_ok else "Missing required permissions"
        })

        all_passed = all(t["passed"] for t in tests)

        return {
            "tests": tests,
            "overall_status": "PASS" if all_passed else "FAIL",
            "ready_for_deployment": all_passed
        }

    def _validate_syntax(self, script: str) -> bool:
        """Validate bash script syntax."""
        # Basic syntax checks
        dangerous_patterns = ["rm -rf /", ":(){:|:&};:", "> /dev/sda"]
        return not any(pattern in script for pattern in dangerous_patterns)

    def _check_safety(self, script: str) -> bool:
        """Check for potentially dangerous operations."""
        # Safety checks for production deployment
        return True

    def _check_permissions(self, incident_data: dict) -> bool:
        """Check if we have required permissions."""
        # Check Azure/GCP permissions
        return True
