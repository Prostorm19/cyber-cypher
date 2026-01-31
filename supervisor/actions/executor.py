"""
Action executor with safety boundaries.
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json

from supervisor.models import (
    ProposedAction, ActionType, Signal, Pattern
)


class ActionExecutor:
    """
    Executes approved actions with safety boundaries.
    
    NEVER modifies:
    - Live checkout behavior
    - Merchant configurations
    - Production code
    
    Only executes with human approval for high-risk actions.
    """
    
    def __init__(self):
        # Registry of action handlers
        self.action_handlers: Dict[ActionType, Callable] = {
            ActionType.DRAFT_SUPPORT_RESPONSE: self._draft_support_response,
            ActionType.ESCALATE_TO_ENGINEERING: self._escalate_to_engineering,
            ActionType.ALERT_SUPPORT_TEAM: self._alert_support_team,
            ActionType.SUGGEST_DOCUMENTATION: self._suggest_documentation,
            ActionType.MONITOR_PATTERN: self._monitor_pattern,
            ActionType.CREATE_INCIDENT_SUMMARY: self._create_incident_summary,
        }
        
        self.execution_log: list[Dict[str, Any]] = []
    
    def execute_action(
        self,
        action: ProposedAction,
        approved: bool = False
    ) -> Dict[str, Any]:
        """
        Execute an action if approved (or if it's low-risk).
        
        Returns execution result with status and details.
        """
        if not approved:
            return {
                "status": "pending_approval",
                "action_type": action.action_type,
                "message": "Action requires human approval before execution"
            }
        
        handler = self.action_handlers.get(action.action_type)
        
        if not handler:
            return {
                "status": "error",
                "action_type": action.action_type,
                "message": f"No handler registered for action type: {action.action_type}"
            }
        
        try:
            result = handler(action)
            
            # Log execution
            self.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action.action_type.value,
                "action_description": action.description,
                "result": result,
                "approved": approved
            })
            
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "action_type": action.action_type,
                "message": f"Execution failed: {str(e)}"
            }
            
            self.execution_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action_type": action.action_type.value,
                "error": str(e)
            })
            
            return error_result
    
    def _draft_support_response(self, action: ProposedAction) -> Dict[str, Any]:
        """Draft a support response (simulated)."""
        issue_category = action.parameters.get("issue_category", "general")
        hypothesis = action.parameters.get("hypothesis", "")
        
        # In production, this would use an LLM to generate contextual responses
        template = self._get_support_template(issue_category, hypothesis)
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "draft_response": template,
            "target_merchants": action.target.split(",") if action.target else [],
            "message": "Support response drafted successfully"
        }
    
    def _escalate_to_engineering(self, action: ProposedAction) -> Dict[str, Any]:
        """Create an engineering escalation (simulated)."""
        escalation = {
            "title": "Migration Issue Escalation",
            "evidence": action.parameters.get("evidence", []),
            "potential_causes": action.parameters.get("potential_causes", []),
            "affected_merchants": action.parameters.get("affected_merchants", []),
            "urgency": action.parameters.get("urgency", "medium"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # In production, this would create a ticket in engineering system
        escalation_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "escalation_id": escalation_id,
            "escalation": escalation,
            "message": f"Escalation {escalation_id} created successfully"
        }
    
    def _alert_support_team(self, action: ProposedAction) -> Dict[str, Any]:
        """Send alert to support team (simulated)."""
        alert = {
            "priority": action.parameters.get("priority", "medium"),
            "affected_merchant_count": action.parameters.get("affected_merchant_count", 0),
            "pattern_description": action.parameters.get("pattern_description", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "alert": alert,
            "message": f"Support team alert sent (priority: {alert['priority']})"
        }
    
    def _suggest_documentation(self, action: ProposedAction) -> Dict[str, Any]:
        """Create documentation suggestion (simulated)."""
        suggestion = {
            "topic": action.parameters.get("topic", "general"),
            "issue_pattern": action.parameters.get("issue_pattern", ""),
            "suggested_content": action.parameters.get("suggested_content", ""),
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "suggestion": suggestion,
            "message": "Documentation suggestion created"
        }
    
    def _monitor_pattern(self, action: ProposedAction) -> Dict[str, Any]:
        """Set up pattern monitoring (simulated)."""
        monitoring = {
            "pattern_ids": action.parameters.get("pattern_ids", []),
            "duration_hours": action.parameters.get("monitoring_duration_hours", 4),
            "trigger_threshold": action.parameters.get("trigger_threshold", ""),
            "started_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "monitoring": monitoring,
            "message": "Pattern monitoring configured"
        }
    
    def _create_incident_summary(self, action: ProposedAction) -> Dict[str, Any]:
        """Create incident summary (simulated)."""
        summary = {
            "pattern_ids": action.parameters.get("pattern_ids", []),
            "signal_ids": action.parameters.get("signal_ids", []),
            "hypothesis": action.parameters.get("hypothesis", ""),
            "created_at": datetime.utcnow().isoformat()
        }
        
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "status": "completed",
            "action_type": action.action_type,
            "incident_id": incident_id,
            "summary": summary,
            "message": f"Incident summary {incident_id} created"
        }
    
    def _get_support_template(self, category: str, hypothesis: str) -> str:
        """Get support response template."""
        templates = {
            "checkout": """
Hi there,

We've identified a pattern of checkout issues that may be related to your recent migration. 
Based on our analysis: {hypothesis}

To resolve this, please:
1. Verify your checkout configuration in the new headless setup
2. Check that authentication tokens are properly configured
3. Review the migration guide section on checkout integration

If issues persist, please provide:
- Your merchant ID
- Screenshots of the issue
- Browser console errors (if any)

We're actively investigating this pattern and will keep you updated.

Best regards,
Support Team
            """,
            "general": """
Hi there,

We've detected a pattern of issues that may be affecting your migration.
{hypothesis}

Our team is investigating and will provide an update shortly. In the meantime, 
please check our migration documentation for common troubleshooting steps.

Best regards,
Support Team
            """
        }
        
        template = templates.get(category, templates["general"])
        return template.format(hypothesis=hypothesis).strip()
    
    def get_execution_log(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """Get execution log."""
        if limit:
            return self.execution_log[-limit:]
        return self.execution_log
    
    def export_execution_log(self, filepath: str) -> None:
        """Export execution log to file."""
        with open(filepath, 'w') as f:
            json.dump(self.execution_log, f, indent=2, default=str)
