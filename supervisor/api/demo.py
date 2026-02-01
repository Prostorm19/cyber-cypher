"""
API endpoint for loading demo/sample data.
"""

from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import List
import random

from supervisor.models import Signal, SignalType, MigrationStage
from supervisor.core.agent import SupervisorAgent

router = APIRouter()


# Dependency to get the agent instance from the server module
def get_agent() -> SupervisorAgent:
    """Get the global agent instance from server."""
    from supervisor.api import server
    return server.agent


def generate_checkout_crisis() -> List[Signal]:
    """
    Generate a realistic checkout crisis scenario.
    Perfect for demonstrating pattern detection and escalation.
    """
    base_time = datetime.utcnow() - timedelta(hours=2)
    signals = []
    
    # 10 merchants affected by checkout authentication issue
    merchant_ids = [f"merchant_{str(i).zfill(3)}" for i in range(1, 11)]
    
    for i, merchant_id in enumerate(merchant_ids):
        # Checkout issues
        signals.append(Signal(
            id=f"demo_checkout_{i}",
            timestamp=base_time + timedelta(minutes=i*5),
            signal_type=SignalType.CHECKOUT_ISSUE,
            merchant_id=merchant_id,
            migration_stage=MigrationStage.MID_MIGRATION,
            description=f"Checkout page blank after migration for {merchant_id}",
            severity="high",
            category="checkout",
            metadata={"source": "demo", "scenario": "checkout_crisis"}
        ))
        
        # Related error logs
        if i < 5:
            signals.append(Signal(
                id=f"demo_error_{i}",
                timestamp=base_time + timedelta(minutes=i*5 + 2),
                signal_type=SignalType.ERROR_LOG,
                merchant_id=merchant_id,
                migration_stage=MigrationStage.MID_MIGRATION,
                description=f"Auth token invalid - checkout authentication failed",
                severity="high",
                category="checkout",
                metadata={"source": "demo", "error_code": "AUTH_INVALID"}
            ))
    
    # Support tickets
    signals.append(Signal(
        id="demo_support_1",
        timestamp=base_time + timedelta(minutes=30),
        signal_type=SignalType.SUPPORT_TICKET,
        merchant_id="merchant_004",
        migration_stage=MigrationStage.MID_MIGRATION,
        description="Multiple customers reporting they can't complete checkout",
        severity="high",
        category="checkout",
        metadata={"source": "demo", "ticket_id": "TICKET-001"}
    ))
    
    return signals


def generate_webhook_issues() -> List[Signal]:
    """Generate webhook failure scenario."""
    base_time = datetime.utcnow() - timedelta(hours=1)
    signals = []
    
    merchants = ["merchant_020", "merchant_021", "merchant_022"]
    
    for i, merchant_id in enumerate(merchants):
        signals.append(Signal(
            id=f"demo_webhook_{i}",
            timestamp=base_time + timedelta(minutes=i*10),
            signal_type=SignalType.WEBHOOK_FAILURE,
            merchant_id=merchant_id,
            migration_stage=MigrationStage.POST_MIGRATION,
            description=f"Order webhook not receiving events for {merchant_id}",
            severity="medium",
            category="webhook",
            metadata={"source": "demo", "webhook_type": "order.created"}
        ))
        
        signals.append(Signal(
            id=f"demo_api_error_{i}",
            timestamp=base_time + timedelta(minutes=i*10 + 5),
            signal_type=SignalType.API_ERROR,
            merchant_id=merchant_id,
            migration_stage=MigrationStage.POST_MIGRATION,
            description="Webhook endpoint returning 401 unauthorized",
            severity="medium",
            category="webhook",
            metadata={"source": "demo", "status_code": 401}
        ))
    
    return signals


def generate_mixed_signals() -> List[Signal]:
    """Generate diverse signals for comprehensive demo."""
    signals = []
    
    # Add checkout crisis
    signals.extend(generate_checkout_crisis())
    
    # Add webhook issues
    signals.extend(generate_webhook_issues())
    
    # Add some normal traffic
    base_time = datetime.utcnow() - timedelta(hours=3)
    
    signals.append(Signal(
        id="demo_normal_1",
        timestamp=base_time,
        signal_type=SignalType.SUPPORT_TICKET,
        merchant_id="merchant_099",
        migration_stage=MigrationStage.PRE_MIGRATION,
        description="When will my migration be scheduled?",
        severity="low",
        category="general",
        metadata={"source": "demo"}
    ))
    
    signals.append(Signal(
        id="demo_normal_2",
        timestamp=base_time + timedelta(minutes=30),
        signal_type=SignalType.MIGRATION_EVENT,
        merchant_id="merchant_100",
        migration_stage=MigrationStage.COMPLETED,
        description="Migration completed successfully",
        severity="low",
        category="migration",
        metadata={"source": "demo", "success": True}
    ))
    
    return signals


@router.get("/demo-scenarios")
async def list_demo_scenarios():
    """List available demo scenarios."""
    return {
        "scenarios": [
            {
                "id": "checkout_crisis",
                "name": "Checkout Authentication Crisis",
                "description": "10 merchants with blank checkout due to auth token issue",
                "signal_count": 15,
                "severity": "high",
                "demonstrates": ["Pattern detection", "High-risk escalation", "GitHub issue creation"]
            },
            {
                "id": "webhook_issues",
                "name": "Webhook Failures",
                "description": "Multiple merchants with webhook delivery failures",
                "signal_count": 6,
                "severity": "medium",
                "demonstrates": ["Medium-risk pattern", "Support alerts"]
            },
            {
                "id": "mixed",
                "name": "Comprehensive Demo",
                "description": "Mix of critical issues and normal traffic",
                "signal_count": 23,
                "severity": "mixed",
                "demonstrates": ["Full system capabilities", "Multi-pattern detection"]
            }
        ]
    }


@router.post("/load-demo-data")
async def load_demo_data(
    scenario: str = "mixed",
    agent: SupervisorAgent = Depends(get_agent)
):
    """
    Load demo/sample data for testing and demonstrations.
    
    Args:
        scenario: Which scenario to load (checkout_crisis, webhook_issues, mixed)
        agent: Injected agent instance from dependency
    
    Returns:
        Summary of loaded data
    """
    # Get scenario data
    scenarios = {
        "checkout_crisis": generate_checkout_crisis,
        "webhook_issues": generate_webhook_issues,
        "mixed": generate_mixed_signals
    }
    
    if scenario not in scenarios:
        return {
            "status": "error",
            "message": f"Unknown scenario: {scenario}",
            "available_scenarios": list(scenarios.keys())
        }
    
    signals = scenarios[scenario]()
    
    # Use the injected global agent instance
    agent.ingest_signals(signals)
    
    return {
        "status": "success",
        "scenario": scenario,
        "signals_loaded": len(signals),
        "message": f"Loaded {len(signals)} demo signals",
        "next_steps": [
            "View signals at /signals",
            "Run analysis at /agent",
            "Check patterns detected"
        ]
    }
