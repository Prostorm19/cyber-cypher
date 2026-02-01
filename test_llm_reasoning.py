"""
Test script to verify LLM-powered reasoning works.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from supervisor.reasoning.llm_client import LLMClient
from supervisor.reasoning.llm_reasoner import LLMReasoner
from supervisor.models import Signal, SignalType, MigrationStage, Pattern
from datetime import datetime, timedelta


def test_llm_client():
    """Test LLM client initialization."""
    print("\n" + "="*60)
    print("  Testing LLM Client")
    print("="*60)
    
    client = LLMClient()
    
    print(f"\nProvider: {client.provider}")
    print(f"Model: {client.model}")
    print(f"Enabled: {client.is_enabled()}")
    
    if not client.is_enabled():
        print("\n⚠️  LLM is DISABLED")
        print("\nTo enable, set in .env:")
        print("  LLM_ENABLED=true")
        print("  OPENAI_API_KEY=your_api_key")
        return False
    
    # Test simple generation
    print("\n📝 Testing text generation...")
    
    response = client.generate(
        "Say 'AI is working!' and nothing else.",
        temperature=0.3,
        max_tokens=20
    )
    
    if response:
        print(f"✅ Response: {response.strip()}")
        return True
    else:
        print("❌ Failed to generate response")
        return False


def test_llm_reasoner():
    """Test LLM reasoner with sample signals."""
    print("\n" + "="*60)
    print("  Testing LLM Reasoner")
    print("="*60)
    
    reasoner = LLMReasoner()
    
    if not reasoner.is_enabled():
        print("\n⚠️  LLM Reasoner is DISABLED (no valid API key)")
        return False
    
    # Create sample signals
    base_time = datetime.utcnow() - timedelta(hours=1)
    
    signals = [
        Signal(
            id=f"test_signal_{i}",
            timestamp=base_time + timedelta(minutes=i*5),
            signal_type=SignalType.CHECKOUT_ISSUE,
            merchant_id=f"merchant_{i:03d}",
            migration_stage=MigrationStage.MID_MIGRATION,
            description=f"Checkout page blank after authentication for merchant {i}",
            severity="high",
            category="checkout",
            metadata={"source": "test"}
        )
        for i in range(1, 6)
    ]
    
    # Create sample pattern
    pattern = Pattern(
        id="test_pattern_1",
        pattern_type="category_migration",
        affected_merchants=[s.merchant_id for s in signals],
        signal_ids=[s.id for s in signals],
        first_seen=signals[0].timestamp,
        last_seen=signals[-1].timestamp,
        frequency=len(signals),
        description="Checkout issues during migration",
        common_attributes={"category": "checkout", "migration_stage": "mid_migration"}
    )
    
    print("\n🧪 Testing hypothesis generation...")
    print(f"Input: {len(signals)} signals,  1 pattern")
    
    hypothesis = reasoner.generate_hypothesis(
        signals=signals,
        detected_patterns=[pattern]
    )
    
    if hypothesis:
        print(f"\n✅ Hypothesis Generated!")
        print(f"\n**Description**: {hypothesis.description}")
        print(f"**Confidence**: {hypothesis.confidence:.0%}")
        print(f"**Evidence**:")
        for i, ev in enumerate(hypothesis.evidence[:3], 1):
            print(f"  {i}. {ev}")
        print(f"**Potential Causes**:")
        for i, cause in enumerate(hypothesis.potential_root_causes[:3], 1):
            print(f"  {i}. {cause}")
        print(f"**LLM Generated**: {hypothesis.llm_generated}")
        return True
    else:
        print("❌ Failed to generate hypothesis")
        return False


def test_confidence_assessment():
    """Test LLM confidence assessment."""
    print("\n" + "="*60)
    print("  Testing Confidence Assessment")
    print("="*60)
    
    reasoner = LLMReasoner()
    
    if not reasoner.is_enabled():
        print("\n⚠️  Skipping (LLM disabled)")
        return False
    
    hypothesis = "Authentication tokens are expiring prematurely during checkout"
    evidence = [
        "10 merchants reporting blank checkout pages",
        "Auth token errors in server logs",
        "All issues started 2 hours ago",
        "Only affects mid-migration merchants"
    ]
    
    signals = []  # Empty for this test
    
    print(f"\nHypothesis: {hypothesis}")
    print(f"Evidence count: {len(evidence)}")
    
    confidence = reasoner.assess_confidence(hypothesis, evidence, signals)
    
    print(f"\n✅ LLM Confidence: {confidence:.0%}")
    return True


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║     LLM REASONING - TEST SUITE                          ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Test 1: LLM Client
    results['LLM Client'] = test_llm_client()
    
    # Test 2: LLM Reasoner
    if results['LLM Client']:
        results['LLM Reasoner'] = test_llm_reasoner()
        results['Confidence Assessment'] = test_confidence_assessment()
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ SKIP/FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 LLM reasoning is working!")
        print("\n💡 The system will now use AI-powered hypothesis generation")
        print("   when LLM_ENABLED=true in your .env file")
    elif passed > 0:
        print("\n⚠️  Some tests passed. LLM may be partially working.")
    else:
        print("\n❌ LLM is disabled or not configured.")
        print("\nTo enable:")
        print("1. Add to .env file:")
        print("   LLM_ENABLED=true")
        print("   OPENAI_API_KEY=your_gemini_or_openai_key")
        print("2. Restart backend server")
