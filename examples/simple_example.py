"""
Simple example of using the supervisor programmatically.
"""

from supervisor.core.agent import SupervisorAgent
from supervisor.models import Signal, SignalType, MigrationStage
from supervisor.memory.manager import MemoryManager
from datetime import datetime


def main():
    # Initialize the supervisor
    agent = SupervisorAgent(confidence_threshold=0.75)
    memory = MemoryManager()
    
    # Create some example signals
    signals = [
        Signal(
            id="sig_001",
            timestamp=datetime.utcnow(),
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id="merchant_123",
            migration_stage=MigrationStage.MID_MIGRATION,
            title="Checkout not working",
            description="Customers can't complete purchases - blank checkout page",
            severity="high",
            category="checkout"
        ),
        Signal(
            id="sig_002",
            timestamp=datetime.utcnow(),
            signal_type=SignalType.ERROR_LOG,
            merchant_id="merchant_123",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="Auth token expired - checkout authentication failed",
            severity="high",
            category="checkout"
        ),
        Signal(
            id="sig_003",
            timestamp=datetime.utcnow(),
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id="merchant_456",
            migration_stage=MigrationStage.MID_MIGRATION,
            title="Payment issues",
            description="Checkout page showing authentication error",
            severity="high",
            category="checkout"
        )
    ]
    
    # Ingest signals
    print("Ingesting signals...")
    agent.ingest_signals(signals)
    print(f"✓ Ingested {len(signals)} signals\n")
    
    # Run agent analysis cycle
    print("Running agent analysis cycle...")
    decision = agent.run_cycle(
        time_window_hours=24,
        auto_approve=False  # Require human approval for high-risk actions
    )
    
    # Print results
    print("\n" + "="*60)
    print("AGENT DECISION")
    print("="*60)
    
    print(f"\nObservations:")
    for obs in decision.observations:
        print(f"  • {obs}")
    
    print(f"\nHypothesis:")
    print(f"  {decision.hypothesis.description}")
    print(f"  Confidence: {decision.hypothesis.confidence:.0%}")
    
    print(f"\nReasoning:")
    print(f"  {decision.reasoning}")
    
    print(f"\nProposed Actions ({len(decision.proposed_actions)}):")
    for i, action in enumerate(decision.proposed_actions, 1):
        print(f"  {i}. {action.action_type.value}")
        print(f"     {action.description}")
    
    print(f"\nRisk Level: {decision.risk_level.value.upper()}")
    print(f"Requires Approval: {'Yes' if decision.requires_human_approval else 'No'}")
    
    print(f"\nExplainability:")
    print(f"  {decision.explainability_notes}")
    
    print("\n" + "="*60)
    
    # If you wanted to approve and execute actions:
    if decision.requires_human_approval:
        print("\n⚠️  Actions require human approval before execution")
        print("To approve, call: agent.executor.execute_action(action, approved=True)")
    else:
        print("\n✓ Actions can be auto-executed (low risk)")
        # Uncomment to actually execute:
        # for action in decision.proposed_actions:
        #     result = agent.executor.execute_action(action, approved=True)
        #     print(f"Executed: {result}")
    
    # Create an incident for tracking
    incident = memory.create_incident(
        title="Checkout authentication issue during migration",
        description=decision.hypothesis.description,
        pattern_ids=decision.hypothesis.affected_patterns,
        signal_ids=[s.id for s in signals]
    )
    print(f"\n✓ Created incident: {incident.id}")


if __name__ == "__main__":
    main()
