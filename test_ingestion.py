"""
Test script for new signal ingestion endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_webhook_generic():
    """Test generic webhook endpoint."""
    print("\n=== Testing Generic Webhook ===")
    
    payload = {
        "signal_type": "checkout_issue",
        "merchant_id": "test_merchant_webhook",
        "migration_stage": "mid_migration",
        "description": "Webhook test: Checkout page not loading",
        "severity": "high",
        "category": "checkout"
    }
    
    response = requests.post(f"{BASE_URL}/signals/webhook", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_webhook_batch():
    """Test webhook with batch signals."""
    print("\n=== Testing Batch Webhook ===")
    
    payload = {
        "signals": [
            {
                "signal_type": "error_log",
                "merchant_id": "merchant_batch_1",
                "migration_stage": "mid_migration",
                "description": "Auth token error",
                "severity": "high",
                "category": "checkout"
            },
            {
                "signal_type": "api_error",
                "merchant_id": "merchant_batch_2",
                "migration_stage": "mid_migration",
                "description": "API authentication failed",
                "severity": "high",
                "category": "checkout"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/signals/webhook", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json()


def test_csv_upload():
    """Test CSV file upload."""
    print("\n=== Testing CSV Upload ===")
    
    with open('test_signals.csv', 'rb') as f:
        files = {'file': ('test_signals.csv', f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/signals/upload/csv", files=files)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()


def check_statistics():
    """Check signal statistics."""
    print("\n=== Checking Statistics ===")
    
    response = requests.get(f"{BASE_URL}/signals/statistics?hours=24")
    stats = response.json()
    print(f"Total signals: {stats.get('total_signals', 0)}")
    print(f"By type: {stats.get('by_type', {})}")
    print(f"By merchant: {stats.get('by_merchant', {})}")
    return stats


if __name__ == "__main__":
    print("Testing Signal Ingestion Endpoints")
    print("=" * 50)
    
    try:
        # Test 1: Generic webhook
        test_webhook_generic()
        
        # Test 2: Batch webhook
        test_webhook_batch()
        
        # Test 3: CSV upload
        test_csv_upload()
        
        # Check results
        stats = check_statistics()
        
        print("\n" + "=" * 50)
        print(f"✅ All tests completed!")
        print(f"Total signals ingested: {stats.get('total_signals', 0)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
