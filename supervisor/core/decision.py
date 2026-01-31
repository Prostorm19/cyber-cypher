"""
Decision engine for selecting appropriate actions based on hypotheses.
"""

from typing import List, Optional
from datetime import datetime

from supervisor.models import (
    Hypothesis, ProposedAction, ActionType, RiskLevel,
    Pattern, Signal, MigrationStage
)


class DecisionEngine:
    """
    Decides what actions to take based on reasoning results.
    Includes confidence scoring and risk assessment.
    """
    
    def __init__(self, confidence_threshold: float = 0.75):
        self.confidence_threshold = confidence_threshold
        
    def decide_actions(
        self,
        hypothesis: Hypothesis,
        patterns: List[Pattern],
        signals: List[Signal]
    ) -> tuple[List[ProposedAction], RiskLevel, bool]:
        """
        Decide what actions to take based on the hypothesis.
        
        Returns:
            - List of proposed actions
            - Overall risk level
            - Whether human approval is required
        """
        proposed_actions = []
        risk_level = self._assess_risk_level(hypothesis, patterns, signals)
        
        # Determine if this involves checkout or money
        involves_checkout = any(
            s.category == "checkout" or s.signal_type.value == "checkout_issue"
            for s in signals
        )
        
        # Human approval required if:
        # - High risk
        # - Checkout/payment involved
        # - Low confidence
        requires_approval = (
            risk_level == RiskLevel.HIGH or
            involves_checkout or
            hypothesis.confidence < self.confidence_threshold
        )
        
        # Action 1: Always create an incident summary
        proposed_actions.append(
            ProposedAction(
                action_type=ActionType.CREATE_INCIDENT_SUMMARY,
                description="Create detailed incident summary with pattern analysis",
                parameters={
                    "pattern_ids": [p.id for p in patterns],
                    "signal_ids": [s.id for s in signals],
                    "hypothesis": hypothesis.description
                },
                expected_impact="Provides documentation and visibility for teams"
            )
        )
        
        # Action 2: Alert support team if multiple merchants affected
        unique_merchants = set()
        for pattern in patterns:
            unique_merchants.update(pattern.affected_merchants)
        
        if len(unique_merchants) >= 3:
            proposed_actions.append(
                ProposedAction(
                    action_type=ActionType.ALERT_SUPPORT_TEAM,
                    description=f"Alert support team about pattern affecting {len(unique_merchants)} merchants",
                    parameters={
                        "priority": "high" if risk_level == RiskLevel.HIGH else "medium",
                        "affected_merchant_count": len(unique_merchants),
                        "pattern_description": patterns[0].description if patterns else ""
                    },
                    expected_impact="Enables proactive support outreach"
                )
            )
        
        # Action 3: Draft support responses for affected merchants
        if hypothesis.confidence >= 0.7 and len(unique_merchants) <= 10:
            proposed_actions.append(
                ProposedAction(
                    action_type=ActionType.DRAFT_SUPPORT_RESPONSE,
                    description="Draft proactive support responses for affected merchants",
                    target=",".join(list(unique_merchants)[:5]),  # First 5 merchants
                    parameters={
                        "issue_category": patterns[0].common_attributes.get("category", "general") if patterns else "general",
                        "hypothesis": hypothesis.description,
                        "confidence": hypothesis.confidence
                    },
                    expected_impact="Provides immediate guidance and reduces ticket volume"
                )
            )
        
        # Action 4: Escalate to engineering if high confidence and significant impact
        if hypothesis.confidence >= 0.75 and (
            len(unique_merchants) >= 5 or risk_level == RiskLevel.HIGH
        ):
            proposed_actions.append(
                ProposedAction(
                    action_type=ActionType.ESCALATE_TO_ENGINEERING,
                    description="Escalate to engineering with evidence and analysis",
                    parameters={
                        "evidence": hypothesis.evidence,
                        "potential_causes": hypothesis.potential_causes,
                        "affected_merchants": list(unique_merchants),
                        "urgency": "high" if risk_level == RiskLevel.HIGH else "medium"
                    },
                    expected_impact="Initiates root cause investigation and fix"
                )
            )
        
        # Action 5: Suggest documentation update if pattern is clear
        if hypothesis.confidence >= 0.8 and "migration" in hypothesis.description.lower():
            proposed_actions.append(
                ProposedAction(
                    action_type=ActionType.SUGGEST_DOCUMENTATION,
                    description="Suggest documentation update to prevent future occurrences",
                    parameters={
                        "topic": patterns[0].common_attributes.get("category", "migration") if patterns else "migration",
                        "issue_pattern": hypothesis.description,
                        "suggested_content": self._generate_doc_suggestion(hypothesis, patterns)
                    },
                    expected_impact="Reduces future support volume through better documentation"
                )
            )
        
        # Action 6: Monitor pattern if confidence is low
        if hypothesis.confidence < self.confidence_threshold:
            proposed_actions.append(
                ProposedAction(
                    action_type=ActionType.MONITOR_PATTERN,
                    description="Continue monitoring pattern before taking action",
                    parameters={
                        "pattern_ids": [p.id for p in patterns],
                        "monitoring_duration_hours": 4,
                        "trigger_threshold": "3 additional occurrences"
                    },
                    expected_impact="Prevents premature action while gathering more evidence"
                )
            )
        
        return proposed_actions, risk_level, requires_approval
    
    def _assess_risk_level(
        self,
        hypothesis: Hypothesis,
        patterns: List[Pattern],
        signals: List[Signal]
    ) -> RiskLevel:
        """Assess the risk level of the situation."""
        risk_score = 0
        
        # Factor 1: Number of affected merchants
        unique_merchants = set()
        for pattern in patterns:
            unique_merchants.update(pattern.affected_merchants)
        
        if len(unique_merchants) >= 10:
            risk_score += 3
        elif len(unique_merchants) >= 5:
            risk_score += 2
        elif len(unique_merchants) >= 3:
            risk_score += 1
        
        # Factor 2: Checkout or payment involvement
        involves_critical = any(
            s.category in ["checkout", "payment"] or
            s.signal_type.value in ["checkout_issue"]
            for s in signals
        )
        if involves_critical:
            risk_score += 2
        
        # Factor 3: Migration stage (mid-migration is higher risk)
        mid_migration_count = sum(
            1 for s in signals
            if s.migration_stage == MigrationStage.MID_MIGRATION
        )
        if mid_migration_count >= len(signals) * 0.5:
            risk_score += 1
        
        # Factor 4: Error severity
        high_severity_count = sum(
            1 for s in signals
            if s.severity and s.severity.lower() in ["high", "critical"]
        )
        if high_severity_count >= 3:
            risk_score += 2
        elif high_severity_count >= 1:
            risk_score += 1
        
        # Convert score to risk level
        if risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _generate_doc_suggestion(
        self,
        hypothesis: Hypothesis,
        patterns: List[Pattern]
    ) -> str:
        """Generate a documentation suggestion."""
        if patterns:
            category = patterns[0].common_attributes.get("category", "general")
            return (
                f"Add troubleshooting guide for {category} issues during migration. "
                f"Include common error: {hypothesis.potential_causes[0] if hypothesis.potential_causes else 'N/A'}"
            )
        return "Add general migration troubleshooting guide"
