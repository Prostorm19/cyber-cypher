"""Test signal ingestion to see the exact error"""
import sys
import json
from datetime import datetime

# Test data matching what frontend sends
test_signal = {
    "signals": [{
        "id": f"sig_{int(datetime.now().timestamp())}",
        "timestamp": datetime.now().isoformat(),
        "signal_type": "checkout_issue",
        "merchant_id": "merchant_test",
        "migration_stage": "mid_migration",
        "category": "checkout",
        "severity": "high",
        "title": "Test signal",
        "description": "Testing signal ingestion"
    }]
}

print("Testing Signal Creation...")
print("=" * 60)
print(json.dumps(test_signal, indent=2))
print("=" * 60)

try:
    from supervisor.models import Signal
    from supervisor.api.server import agent
    
    print("\n1. Creating Signal object...")
    signal_data = test_signal["signals"][0]
    signal = Signal(**signal_data)
    print(f"✓ Signal created: {signal.id}")
    
    print("\n2. Ingesting into agent...")
    agent.ingest_signal(signal)
    print("✓ Signal ingested successfully")
    
    print("\n3. Checking signal storage...")
    recent = agent.observation.get_recent_signals(hours=24)
    print(f"✓ Total signals in memory: {len(recent)}")
    
    print("\n✅ ALL TESTS PASSED - Signal ingestion works!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
