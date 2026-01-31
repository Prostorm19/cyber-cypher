"""
Tests for the reasoning engine.
"""

import pytest
from datetime import datetime, timedelta

from supervisor.core.observation import ObservationEngine
from supervisor.reasoning.engine import ReasoningEngine
from supervisor.models import Signal, SignalType, MigrationStage


@pytest.fixture
def reasoning_engine():
    obs = ObservationEngine()
    return ReasoningEngine(obs)


@pytest.fixture
def pattern_signals():
    """Signals that should form a clear pattern."""
    base_time = datetime.utcnow()
    
    return [
        Signal(
            id=f"sig_{i}",
            timestamp=base_time - timedelta(minutes=i*10),
            signal_type=SignalType.ERROR_LOG,
            merchant_id=f"merchant_{i}",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="Auth token invalid - checkout failed",
            severity="high",
            category="checkout"
        )
        for i in range(5)  # 5 merchants with same issue
    ]


def test_detect_category_migration_patterns(reasoning_engine, pattern_signals):
    """Test detection of category+migration stage patterns."""
    reasoning_engine.observation.ingest_signals(pattern_signals)
    
    patterns = reasoning_engine.detect_patterns(
        time_window_hours=24,
        min_frequency=3
    )
    
    # Should detect at least one pattern
    assert len(patterns) > 0
    
    # Pattern should have multiple affected merchants
    assert len(patterns[0].affected_merchants) >= 3


def test_detect_error_patterns(reasoning_engine, pattern_signals):
    """Test detection of error patterns."""
    reasoning_engine.observation.ingest_signals(pattern_signals)
    
    patterns = reasoning_engine.detect_patterns(min_frequency=2)
    
    # Should detect error pattern with "auth" keyword
    error_patterns = [p for p in patterns if p.pattern_type == "error_cluster"]
    assert len(error_patterns) > 0


def test_formulate_hypothesis(reasoning_engine, pattern_signals):
    """Test hypothesis formulation."""
    reasoning_engine.observation.ingest_signals(pattern_signals)
    
    patterns = reasoning_engine.detect_patterns(min_frequency=2)
    hypothesis = reasoning_engine.formulate_hypothesis(patterns, pattern_signals)
    
    assert hypothesis is not None
    assert hypothesis.confidence > 0
    assert len(hypothesis.evidence) > 0
    assert len(hypothesis.potential_causes) > 0


def test_hypothesis_confidence_scoring(reasoning_engine, pattern_signals):
    """Test that confidence increases with stronger evidence."""
    reasoning_engine.observation.ingest_signals(pattern_signals)
    
    patterns = reasoning_engine.detect_patterns(min_frequency=2)
    hypothesis = reasoning_engine.formulate_hypothesis(patterns, pattern_signals)
    
    # With 5 merchants in same stage showing same error, confidence should be high
    assert hypothesis.confidence >= 0.7


def test_no_pattern_detection_with_insufficient_data(reasoning_engine):
    """Test that no patterns are detected with insufficient data."""
    # Only 1 signal - not enough for a pattern
    signal = Signal(
        id="sig_1",
        timestamp=datetime.utcnow(),
        signal_type=SignalType.SUPPORT_TICKET,
        merchant_id="merchant_1",
        migration_stage=MigrationStage.MID_MIGRATION,
        description="Issue",
        category="general"
    )
    
    reasoning_engine.observation.ingest_signal(signal)
    
    patterns = reasoning_engine.detect_patterns(min_frequency=2)
    
    assert len(patterns) == 0
