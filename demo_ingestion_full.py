"""
Complete end-to-end demo showing real signal ingestion working.
Run this after restarting the backend server.
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_1_webhook():
    """Test 1: Webhook ingestion"""
    print_header("TEST 1: Webhook Ingestion")
    
    payload = {
        "signal_type": "checkout_issue",
        "merchant_id": "webhook_merchant_1",
        "migration_stage": "mid_migration",
        "description": "Webhook test: Checkout authentication failed",
        "severity": "high",
        "category": "checkout"
    }
    
    print(f"Sending webhook: {payload['description']}")
    response = requests.post(f"{BASE_URL}/signals/webhook", json=payload)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Success! Signal ID: {result['signal_ids'][0]}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
    
    return response.status_code == 201


def test_2_csv_upload():
    """Test 2: CSV file upload"""
    print_header("TEST 2: CSV File Upload")
    
    print("Uploading test_signals.csv (10 signals)...")
    
    with open('test_signals.csv', 'rb') as f:
        files = {'file': ('test_signals.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/signals/upload/csv", files=files)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Success! Ingested {len(result['signal_ids'])} signals")
            print(f"   File: {result['filename']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
        
        return response.status_code == 201


def test_3_check_signals():
    """Test 3: Verify signals were ingested"""
    print_header("TEST 3: Verify Signal Statistics")
    
    response = requests.get(f"{BASE_URL}/signals/statistics?hours=24")
    stats = response.json()
    
    print(f"Total signals: {stats.get('total_signals', 0)}")
    print(f"\nBy type:")
    for sig_type, count in stats.get('by_type', {}).items():
        print(f"  - {sig_type}: {count}")
    
    print(f"\nBy migration stage:")
    for stage, count in stats.get('by_stage', {}).items():
        print(f"  - {stage}: {count}")
    
    return stats.get('total_signals', 0) > 0


def test_4_run_analysis():
    """Test 4: Run agent analysis on ingested signals"""
    print_header("TEST 4: Run Agent Analysis")
    
    print("Running agent cycle (OBSERVE → REASON → DECIDE)...")
    
    response = requests.post(f"{BASE_URL}/agent/analyze", json={
        "time_window_hours": 24,
        "auto_approve": False
    })
    
    if response.status_code == 200:
        decision = response.json()
        
        hypothesis = decision.get('hypothesis', {})
        print(f"\n✅ Analysis complete!")
        print(f"\nHypothesis: {hypothesis.get('description', 'N/A')}")
        print(f"Confidence: {hypothesis.get('confidence', 0) * 100:.0f}%")
        print(f"Risk Level: {decision.get('risk_level', 'N/A')}")
        print(f"Requires Approval: {decision.get('requires_approval', False)}")
        print(f"\nProposed Actions: {len(decision.get('proposed_actions', []))}")
        
        for i, action in enumerate(decision.get('proposed_actions', [])[:3], 1):
            print(f"  {i}. {action.get('action_type', 'N/A')}: {action.get('description', 'N/A')}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        return False


def test_5_check_dashboard():
    """Test 5: Provide dashboard links"""
    print_header("TEST 5: Check Dashboard")
    
    print("\n📊 View results in web UI:")
    print(f"   Dashboard:  http://localhost:3000")
    print(f"   Signals:    http://localhost:3000/signals")
    print(f"   Upload:     http://localhost:3000/signals/upload")
    print(f"   Agent:      http://localhost:3000/agent")
    print(f"   Actions:    http://localhost:3000/actions")
    
    return True


if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║     CYBER CYPHER - END-TO-END INGESTION DEMO              ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    results = []
    
    try:
        # Run tests
        results.append(("Webhook Ingestion", test_1_webhook()))
        time.sleep(0.5)
        
        results.append(("CSV Upload", test_2_csv_upload()))
        time.sleep(0.5)
        
        results.append(("Signal Verification", test_3_check_signals()))
        time.sleep(0.5)
        
        results.append(("Agent Analysis", test_4_run_analysis()))
        time.sleep(0.5)
        
        results.append(("Dashboard Links", test_5_check_dashboard()))
        
        # Summary
        print_header("DEMO SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\nResults: {passed}/{total} tests passed\n")
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status}  {test_name}")
        
        if passed == total:
            print("\n🎉 All tests passed! System working end-to-end!")
            print("\n💡 Next: Open http://localhost:3000/signals/upload and try uploading!")
        else:
            print("\n⚠️  Some tests failed. Check if backend server is running.")
            print("   Run: python -m supervisor.api.server")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("\n   Make sure the backend is running:")
        print("   cd c:\\ROSHITH2\\Projects\\cyber-cypher")
        print("   .\\venv\\Scripts\\activate")
        print("   python -m supervisor.api.server")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
