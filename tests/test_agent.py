"""
Tests for the agent orchestrator.
"""

import pytest
from datetime import datetime, timedelta

from supervisor.core.agent import SupervisorAgent
from supervisor.models import Signal, SignalType, MigrationStage, RiskLevel


@pytest.fixture
def agent():
    return SupervisorAgent(confidence_threshold=0.75)


@pytest.fixture
def crisis_signals():
    """Signals representing a crisis scenario."""
    base_time = datetime.utcnow()
    
    return [
        Signal(
            id=f"sig_checkout_{i}",
            timestamp=base_time - timedelta(minutes=i*15),
            signal_type=SignalType.CHECKOUT_ISSUE,
            merchant_id=f"merchant_{i}",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="Checkout page blank - auth token issue",
            severity="high",
            category="checkout"
        )
        for i in range(6)  # 6 merchants affected
    ]


def test_agent_run_cycle(agent, crisis_signals):
    """Test full agent cycle execution."""
    agent.ingest_signals(crisis_signals)
    
    decision = agent.run_cycle(time_window_hours=24, auto_approve=False)
    
    # Should produce a decision
    assert decision is not None
    assert len(decision.observations) > 0
    assert decision.hypothesis is not None


def test_agent_detects_high_risk(agent, crisis_signals):
    """Test that agent correctly identifies high-risk situations."""
    agent.ingest_signals(crisis_signals)
    
    decision = agent.run_cycle()
    
    # Checkout issues with multiple merchants should be high risk
    assert decision.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]
    assert decision.requires_human_approval is True


def test_agent_proposes_actions(agent, crisis_signals):
    """Test that agent proposes appropriate actions."""
    agent.ingest_signals(crisis_signals)
    
    decision = agent.run_cycle()
    
    # Should propose multiple actions
    assert len(decision.proposed_actions) > 0
    
    # Should include incident summary
    action_types = [a.action_type.value for a in decision.proposed_actions]
    assert "create_incident_summary" in action_types


def test_agent_low_confidence_monitoring(agent):
    """Test that low confidence leads to monitoring recommendation."""
    # Create ambiguous signals
    signals = [
        Signal(
            id="sig_1",
            timestamp=datetime.utcnow(),
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id="merchant_1",
            migration_stage=MigrationStage.PRE_MIGRATION,
            description="Question about pricing",
            category="general"
        ),
        Signal(
            id="sig_2",
            timestamp=datetime.utcnow(),
            signal_type=SignalType.ERROR_LOG,
            merchant_id="merchant_2",
            migration_stage=MigrationStage.POST_MIGRATION,
            description="Minor warning log",
            category="logs"
        )
    ]
    
    agent.ingest_signals(signals)
    decision = agent.run_cycle()
    
    # Should have low confidence
    assert decision.hypothesis.confidence < 0.75


def test_decision_history_tracking(agent, crisis_signals):
    """Test that decision history is tracked."""
    agent.ingest_signals(crisis_signals)
    
    decision1 = agent.run_cycle()
    decision2 = agent.run_cycle()
    
    history = agent.get_decision_history()
    
    assert len(history) == 2
    assert history[0] == decision1
    assert history[1] == decision2


def test_agent_explainability(agent, crisis_signals):
    """Test that agent provides explainability."""
    agent.ingest_signals(crisis_signals)
    
    decision = agent.run_cycle()
    
    # Should have reasoning and explainability notes
    assert len(decision.reasoning) > 0
    assert len(decision.explainability_notes) > 0
    
    # Should explain confidence
    assert "confidence" in decision.explainability_notes.lower()
