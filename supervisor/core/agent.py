"""
Main agent orchestrator - implements the observe-reason-decide-act-explain loop.
"""

from typing import List, Optional
from datetime import datetime

from supervisor.models import (
    Signal, AgentDecision, Hypothesis, RiskLevel
)
from supervisor.core.observation import ObservationEngine
from supervisor.reasoning.engine import ReasoningEngine
from supervisor.core.decision import DecisionEngine
from supervisor.actions.executor import ActionExecutor
from supervisor.config import settings


class SupervisorAgent:
    """
    Main supervisor agent that orchestrates the full agent loop:
    OBSERVE -> REASON -> DECIDE -> ACT -> EXPLAIN
    """
    
    def __init__(
        self,
        confidence_threshold: Optional[float] = None,
        memory_retention_days: Optional[int] = None
    ):
        # Initialize all engines
        self.observation = ObservationEngine(
            memory_retention_days=memory_retention_days or settings.max_short_term_memory_days
        )
        self.reasoning = ReasoningEngine(self.observation)
        self.decision = DecisionEngine(
            confidence_threshold=confidence_threshold or settings.confidence_threshold
        )
        self.executor = ActionExecutor()
        
        self.decision_history: List[AgentDecision] = []
    
    def run_cycle(
        self,
        signals: Optional[List[Signal]] = None,
        time_window_hours: int = 24,
        auto_approve: bool = False
    ) -> AgentDecision:
        """
        Run a complete agent cycle: observe, reason, decide, act, explain.
        
        Args:
            signals: Optional new signals to ingest
            time_window_hours: Time window for analysis
            auto_approve: Whether to auto-approve low-risk actions
            
        Returns:
            AgentDecision with full explainability
        """
        
        # 1. OBSERVE
        observations = self._observe(signals, time_window_hours)
        
        # 2. REASON
        patterns = self.reasoning.detect_patterns(
            time_window_hours=time_window_hours,
            min_frequency=settings.min_pattern_frequency
        )
        
        recent_signals = self.observation.get_recent_signals(hours=time_window_hours)
        hypothesis = self.reasoning.formulate_hypothesis(patterns, recent_signals)
        
        # 3. DECIDE
        if hypothesis:
            proposed_actions, risk_level, requires_approval = self.decision.decide_actions(
                hypothesis, patterns, recent_signals
            )
        else:
            # No clear hypothesis - monitor only
            hypothesis = Hypothesis(
                description="No significant patterns detected",
                confidence=0.0,
                evidence=["Insufficient data or no clear patterns in recent signals"],
                potential_causes=[],
                uncertainty_notes="Normal operation - continue monitoring"
            )
            proposed_actions = []
            risk_level = RiskLevel.LOW
            requires_approval = False
        
        # 4. ACT (conditionally)
        if auto_approve and not requires_approval and risk_level == RiskLevel.LOW:
            for action in proposed_actions:
                self.executor.execute_action(action, approved=True)
        
        # 5. EXPLAIN
        decision = AgentDecision(
            observations=observations,
            hypothesis=hypothesis,
            reasoning=self._generate_reasoning_explanation(
                hypothesis, patterns, recent_signals
            ),
            proposed_actions=proposed_actions,
            risk_level=risk_level,
            requires_human_approval=requires_approval,
            explainability_notes=self._generate_explainability_notes(
                hypothesis, risk_level, requires_approval
            )
        )
        
        # Store decision
        self.decision_history.append(decision)
        
        return decision
    
    def _observe(
        self,
        new_signals: Optional[List[Signal]],
        time_window_hours: int
    ) -> List[str]:
        """Observe and ingest signals, return human-readable observations."""
        if new_signals:
            self.observation.ingest_signals(new_signals)
        
        stats = self.observation.get_signal_statistics(hours=time_window_hours)
        
        observations = [
            f"Analyzed {stats['total_signals']} signals from past {time_window_hours} hours"
        ]
        
        if stats['unique_merchants'] > 0:
            observations.append(
                f"{stats['unique_merchants']} unique merchants affected"
            )
        
        # Add signal type breakdown
        if stats['by_type']:
            top_types = sorted(
                stats['by_type'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            
            type_summary = ", ".join([f"{count} {t}" for t, count in top_types])
            observations.append(f"Signal breakdown: {type_summary}")
        
        # Add migration stage breakdown
        if stats['by_migration_stage']:
            stage_summary = ", ".join([
                f"{count} in {stage}"
                for stage, count in stats['by_migration_stage'].items()
            ])
            observations.append(f"Migration stages: {stage_summary}")
        
        return observations
    
    def _generate_reasoning_explanation(
        self,
        hypothesis: Hypothesis,
        patterns: List,
        signals: List[Signal]
    ) -> str:
        """Generate detailed reasoning explanation."""
        if hypothesis.confidence == 0.0:
            return "No significant patterns detected in current time window. System operating normally."
        
        reasoning_parts = [
            f"Detected {len(patterns)} pattern(s) across {len(signals)} signals.",
        ]
        
        if patterns:
            reasoning_parts.append(
                f"Primary pattern: {patterns[0].description}"
            )
        
        reasoning_parts.append(
            f"Confidence level: {hypothesis.confidence:.0%} based on: " +
            "; ".join(hypothesis.evidence[:3])  # Top 3 evidence items
        )
        
        if hypothesis.potential_causes:
            reasoning_parts.append(
                f"Most likely cause: {hypothesis.potential_causes[0]}"
            )
        
        return " ".join(reasoning_parts)
    
    def _generate_explainability_notes(
        self,
        hypothesis: Hypothesis,
        risk_level: RiskLevel,
        requires_approval: bool
    ) -> str:
        """Generate explainability notes explaining the decision process."""
        notes = []
        
        # Explain confidence
        if hypothesis.confidence >= 0.8:
            notes.append("High confidence due to strong pattern evidence and correlation.")
        elif hypothesis.confidence >= settings.confidence_threshold:
            notes.append("Moderate-high confidence - pattern is clear but some uncertainty remains.")
        else:
            notes.append(
                f"Confidence below threshold ({settings.confidence_threshold:.0%}) - "
                "recommending monitoring before action."
            )
        
        # Explain risk assessment
        if risk_level == RiskLevel.HIGH:
            notes.append(
                "Risk assessed as HIGH due to checkout/payment involvement or large merchant impact."
            )
        elif risk_level == RiskLevel.MEDIUM:
            notes.append(
                "Risk assessed as MEDIUM - multiple merchants affected but not critical systems."
            )
        else:
            notes.append("Risk assessed as LOW - limited scope and non-critical systems.")
        
        # Explain approval requirement
        if requires_approval:
            reasons = []
            if risk_level == RiskLevel.HIGH:
                reasons.append("high risk level")
            if hypothesis.confidence < settings.confidence_threshold:
                reasons.append("confidence below threshold")
            
            notes.append(
                f"Human approval required due to: {', '.join(reasons) if reasons else 'safety policy'}."
            )
        else:
            notes.append("Actions can be auto-executed as risk is low and confidence is sufficient.")
        
        # Add uncertainty notes
        if hypothesis.uncertainty_notes:
            notes.append(f"Uncertainty: {hypothesis.uncertainty_notes}")
        
        return " ".join(notes)
    
    def get_decision_history(self, limit: Optional[int] = None) -> List[AgentDecision]:
        """Get decision history."""
        if limit:
            return self.decision_history[-limit:]
        return self.decision_history
    
    def ingest_signal(self, signal: Signal) -> None:
        """Convenience method to ingest a single signal."""
        self.observation.ingest_signal(signal)
    
    def ingest_signals(self, signals: List[Signal]) -> None:
        """Convenience method to ingest multiple signals."""
        self.observation.ingest_signals(signals)
