"""Tester Agent for Tines Story Factory.

Validates the generated story specification:
- Completeness check
- Consistency verification
- Security review
- Best practices validation
"""
from .base import TinesBaseAgent, TinesAgentState


class TinesTesterAgent(TinesBaseAgent):
    """Tester agent that validates Tines story specifications."""
    
    def __init__(self):
        super().__init__(
            name="TinesTester",
            description="Validates Tines story specifications"
        )
    
    async def process(self, state: TinesAgentState) -> dict:
        """Test and validate the story specification."""
        self._log("Testing story specification")
        
        # Run validation tests
        validation_results = self._run_validation(state)
        
        # Find issues
        issues = self._find_issues(state, validation_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, state)
        
        # Determine if ready for deployment
        is_valid = len([i for i in issues if i["severity"] == "critical"]) == 0
        
        self._log(f"Validation: {'PASSED' if is_valid else 'FAILED'} - {len(issues)} issues found")
        
        return {
            "validation_results": validation_results,
            "issues_found": issues,
            "recommendations": recommendations,
            "agent_results": {
                **state.agent_results,
                "tester": {
                    "validation_passed": is_valid,
                    "issues_count": len(issues),
                    "status": "completed"
                }
            }
        }
    
    def _run_validation(self, state: TinesAgentState) -> dict:
        """Run validation checks on the specification."""
        results = {
            "completeness": self._check_completeness(state),
            "consistency": self._check_consistency(state),
            "security": self._check_security(state),
            "best_practices": self._check_best_practices(state)
        }
        
        # Calculate overall score
        total = sum(r["score"] for r in results.values())
        results["overall_score"] = total / len(results)
        
        return results
    
    def _check_completeness(self, state: TinesAgentState) -> dict:
        """Check if specification is complete."""
        issues = []
        score = 100
        
        # Check required fields
        if not state.story_spec.get("name"):
            issues.append("Story name is missing")
            score -= 20
        
        if not state.story_spec.get("description"):
            issues.append("Story description is missing")
            score -= 10
        
        # Check actions
        if not state.actions_json:
            issues.append("No actions defined")
            score -= 30
        elif len(state.actions_json) < 3:
            issues.append("Too few actions (minimum recommended: 3)")
            score -= 15
        
        # Check trigger
        has_trigger = any(a["type"] == "WebhookAgent" for a in state.actions_json)
        if not has_trigger:
            issues.append("No trigger action defined")
            score -= 25
        
        return {
            "score": max(0, score),
            "issues": issues,
            "passed": score >= 70
        }
    
    def _check_consistency(self, state: TinesAgentState) -> dict:
        """Check consistency between components."""
        issues = []
        score = 100
        
        # Check data flow consistency
        data_flow = state.data_flow
        actions = {a["name"] for a in state.actions_json}
        
        for action_name, flow in data_flow.items():
            # Check if inputs are valid
            for inp in flow.get("inputs", []):
                if inp["from"] not in actions:
                    issues.append(f"Data flow references unknown action: {inp['from']}")
                    score -= 10
            
            # Check if next actions exist
            for next_action in flow.get("next", []):
                if next_action not in actions:
                    issues.append(f"Data flow references unknown next action: {next_action}")
                    score -= 10
        
        # Check action references
        for action in state.actions_json:
            if action.get("approval", {}).get("required"):
                if not action.get("approval", {}).get("approver"):
                    issues.append(f"Approval gate without approver: {action['name']}")
                    score -= 15
        
        return {
            "score": max(0, score),
            "issues": issues,
            "passed": score >= 70
        }
    
    def _check_security(self, state: TinesAgentState) -> dict:
        """Check security aspects."""
        issues = []
        score = 100
        
        # Check for destructive actions without approval
        destructive_types = ["MicrosoftGraphAgent", "HTTPAgent"]
        destructive_actions = [
            a for a in state.actions_json 
            if a["type"] in destructive_types and 
            any(x in a.get("name", "").lower() for x in ["delete", "remove", "block", "disable"])
        ]
        
        for action in destructive_actions:
            if not action.get("approval", {}).get("required"):
                issues.append(f"Destructive action without approval: {action['name']}")
                score -= 20
        
        # Check for credentials usage
        needed = set(state.credentials_needed)
        if not needed:
            issues.append("No credentials required - may need authentication")
            score -= 5
        
        return {
            "score": max(0, score),
            "issues": issues,
            "passed": score >= 60
        }
    
    def _check_best_practices(self, state: TinesAgentState) -> dict:
        """Check adherence to best practices."""
        issues = []
        score = 100
        
        # Check action naming
        for action in state.actions_json:
            if not action.get("name"):
                issues.append("Action without name")
                score -= 5
            elif len(action["name"]) < 3:
                issues.append(f"Action name too short: {action['name']}")
                score -= 5
        
        # Check layer assignment
        layers = set(a.get("layer") for a in state.actions_json if a.get("layer"))
        if not layers:
            issues.append("No layers defined")
            score -= 15
        
        # Check for logging/error handling
        has_error_handling = any(
            "error" in a.get("name", "").lower() or 
            "catch" in a.get("name", "").lower()
            for a in state.actions_json
        )
        
        if not has_error_handling:
            issues.append("No error handling action defined")
            score -= 10
        
        return {
            "score": max(0, score),
            "issues": issues,
            "passed": score >= 70
        }
    
    def _find_issues(self, state: TinesAgentState, validation_results: dict) -> list:
        """Collect all issues found during validation."""
        issues = []
        
        for check_name, result in validation_results.items():
            if check_name == "overall_score":
                continue
            
            for issue in result.get("issues", []):
                issues.append({
                    "check": check_name,
                    "issue": issue,
                    "severity": self._determine_severity(issue)
                })
        
        return issues
    
    def _determine_severity(self, issue: str) -> str:
        """Determine severity of an issue."""
        critical_keywords = ["missing", "no trigger", "no action"]
        warning_keywords = ["without approval", "too few", "no error"]
        
        issue_lower = issue.lower()
        
        for kw in critical_keywords:
            if kw in issue_lower:
                return "critical"
        
        for kw in warning_keywords:
            if kw in issue_lower:
                return "warning"
        
        return "info"
    
    def _generate_recommendations(self, issues: list, state: TinesAgentState) -> list:
        """Generate recommendations based on issues."""
        recommendations = []
        
        # Group by severity
        critical = [i for i in issues if i["severity"] == "critical"]
        warnings = [i for i in issues if i["severity"] == "warning"]
        
        if critical:
            recommendations.append({
                "priority": "high",
                "text": f"Fix {len(critical)} critical issue(s) before deployment"
            })
        
        if not any("approval" in i["issue"].lower() for i in issues):
            recommendations.append({
                "priority": "medium",
                "text": "Consider adding more approval gates for safety"
            })
        
        if len(state.actions_json) > 20:
            recommendations.append({
                "priority": "low",
                "text": "Consider splitting into multiple sub-stories for maintainability"
            })
        
        recommendations.append({
            "priority": "info",
            "text": "Review story in Tines UI before enabling"
        })
        
        return recommendations
