"""
Tests for the observation engine.
"""

import pytest
from datetime import datetime, timedelta

from supervisor.core.observation import ObservationEngine
from supervisor.models import Signal, SignalType, MigrationStage


@pytest.fixture
def observation_engine():
    return ObservationEngine(memory_retention_days=7)


@pytest.fixture
def sample_signals():
    base_time = datetime.utcnow()
    return [
        Signal(
            id="sig_1",
            timestamp=base_time - timedelta(hours=1),
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id="merchant_1",
            migration_stage=MigrationStage.MID_MIGRATION,
            title="Checkout issue",
            description="Checkout not loading",
            category="checkout"
        ),
        Signal(
            id="sig_2",
            timestamp=base_time - timedelta(hours=2),
            signal_type=SignalType.ERROR_LOG,
            merchant_id="merchant_2",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="Auth token invalid",
            category="checkout"
        ),
        Signal(
            id="sig_3",
            timestamp=base_time - timedelta(hours=25),  # Older than 24h
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id="merchant_3",
            migration_stage=MigrationStage.PRE_MIGRATION,
            title="General question",
            description="Migration timeline query",
            category="general"
        )
    ]


def test_ingest_signal(observation_engine, sample_signals):
    """Test signal ingestion."""
    observation_engine.ingest_signal(sample_signals[0])
    
    assert len(observation_engine.signals) == 1
    assert "sig_1" in observation_engine.signals


def test_ingest_multiple_signals(observation_engine, sample_signals):
    """Test multiple signal ingestion."""
    observation_engine.ingest_signals(sample_signals)
    
    assert len(observation_engine.signals) == 3


def test_get_recent_signals(observation_engine, sample_signals):
    """Test retrieving recent signals."""
    observation_engine.ingest_signals(sample_signals)
    
    recent = observation_engine.get_recent_signals(hours=24)
    
    # Should only get sig_1 and sig_2 (sig_3 is older than 24h)
    assert len(recent) == 2
    assert all(s.id in ["sig_1", "sig_2"] for s in recent)


def test_get_signals_by_type(observation_engine, sample_signals):
    """Test filtering signals by type."""
    observation_engine.ingest_signals(sample_signals)
    
    tickets = observation_engine.get_recent_signals(
        hours=30,
        signal_type=SignalType.SUPPORT_TICKET
    )
    
    assert len(tickets) == 2
    assert all(s.signal_type == SignalType.SUPPORT_TICKET for s in tickets)


def test_get_signals_by_merchant(observation_engine, sample_signals):
    """Test filtering signals by merchant."""
    observation_engine.ingest_signals(sample_signals)
    
    merchant_signals = observation_engine.get_signals_by_merchant("merchant_1")
    
    assert len(merchant_signals) == 1
    assert merchant_signals[0].merchant_id == "merchant_1"


def test_group_signals_by_attribute(observation_engine, sample_signals):
    """Test grouping signals by attribute."""
    observation_engine.ingest_signals(sample_signals)
    
    by_stage = observation_engine.group_signals_by_attribute(
        sample_signals,
        "migration_stage"
    )
    
    assert MigrationStage.MID_MIGRATION in by_stage
    assert len(by_stage[MigrationStage.MID_MIGRATION]) == 2


def test_signal_statistics(observation_engine, sample_signals):
    """Test signal statistics generation."""
    observation_engine.ingest_signals(sample_signals)
    
    stats = observation_engine.get_signal_statistics(hours=30)
    
    assert stats["total_signals"] == 3
    assert stats["unique_merchants"] == 3
    assert "by_type" in stats
    assert "by_migration_stage" in stats
