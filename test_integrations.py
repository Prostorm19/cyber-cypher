"""
Test script for GitHub and Slack integrations.
Tests real issue creation and Slack alerts.
"""

import os
from supervisor.integrations import GitHubClient, SlackClient


def test_github():
    """Test GitHub integration."""
    print("\n" + "="*60)
    print("  Testing GitHub Integration")
    print("="*60)
    
    github = GitHubClient()
    
    if not github.is_enabled():
        print("\n❌ GitHub integration is DISABLED")
        print("\nTo enable:")
        print("1. Create GitHub personal access token:")
        print("   https://github.com/settings/tokens")
        print("2. Add to .env file:")
        print("   GITHUB_TOKEN=ghp_your_token_here")
        print("   GITHUB_REPO=yourusername/repo-name")
        print("   GITHUB_ENABLED=true")
        return False
    
    print(f"\n✅ GitHub client initialized")
    print(f"   Repo: {github.repo_name}")
    
    # Test issue creation
    print("\n📝 Creating test issue...")
    
    result = github.create_issue(
        title="[TEST] Cyber Cypher Integration Test",
        body="This is a test issue created by the Cyber Cypher integration test script.\n\nYou can safely close this issue.",
        labels=["test", "integration"]
    )
    
    if result.get('status') == 'success':
        print(f"✅ Issue created successfully!")
        print(f"   Issue #: {result['issue_number']}")
        print(f"   URL: {result['issue_url']}")
        return True
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
        return False


def test_slack():
    """Test Slack integration."""
    print("\n" + "="*60)
    print("  Testing Slack Integration")
    print("="*60)
    
    slack = SlackClient()
    
    if not slack.is_enabled():
        print("\n❌ Slack integration is DISABLED")
        print("\nTo enable:")
        print("1. Create Slack incoming webhook:")
        print("   https://api.slack.com/messaging/webhooks")
        print("2. Add to .env file:")
        print("   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...")
        print("   SLACK_ENABLED=true")
        return False
    
    print(f"\n✅ Slack client initialized")
    
    # Test simple message
    print("\n📨 Sending test message...")
    
    result = slack.send_message(
        text="Test message from Cyber Cypher integration test"
    )
    
    if result.get('status') == 'success':
        print(f"✅ Message sent successfully!")
        print(f"   Check your Slack channel for the message")
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
        return False
    
    # Test formatted alert
    print("\n🚨 Sending test alert...")
    
    result = slack.send_alert(
        priority="medium",
        message="Test alert from Cyber Cypher",
        details={
            "Test Type": "Integration Test",
            "Status": "Working"
        }
    )
    
    if result.get('status') == 'success':
        print(f"✅ Alert sent successfully!")
        return True
    else:
        print(f"❌ Failed: {result.get('message', 'Unknown error')}")
        return False


def test_escalation_flow():
    """Test full escalation flow (GitHub + Slack)."""
    print("\n" + "="*60)
    print("  Testing Full Escalation Flow")
    print("="*60)
    
    github = GitHubClient()
    slack = SlackClient()
    
    if not github.is_enabled():
        print("\n⚠️  Skipping escalation test (GitHub disabled)")
        return False
    
    # Create escalation issue
    print("\n📋 Creating escalation issue...")
    
    body = github.format_escalation_body(
        hypothesis="Checkout authentication tokens expiring prematurely",
        evidence=[
            "10 merchants reporting blank checkout pages",
            "Auth token errors in logs",
            "Pattern started 2 hours ago"
        ],
        affected_merchants=["merchant_001", "merchant_002", "merchant_003"],
        potential_causes=[
            "Token TTL misconfiguration",
            "Session storage issue"
        ],
        confidence=0.85
    )
    
    result = github.create_issue(
        title="[ESCALATION] Checkout authentication issue",
        body=body,
        labels=["escalation", "migration", "test"]
    )
    
    if result.get('status') != 'success':
        print(f"❌ GitHub failed: {result.get('message')}")
        return False
    
    print(f"✅ Escalation issue created: {result['issue_url']}")
    
    # Send Slack notification
    if slack.is_enabled():
        print("\n📢 Sending Slack notification...")
        
        slack_result = slack.send_escalation_notification(
            hypothesis="Checkout authentication issue",
            confidence=0.85,
            affected_merchants_count=10,
            github_issue_url=result['issue_url']
        )
        
        if slack_result.get('status') == 'success':
            print(f"✅ Slack notification sent!")
        else:
            print(f"⚠️  Slack failed: {slack_result.get('message')}")
    
    return True


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║     CYBER CYPHER - INTEGRATION TEST SUITE               ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = {}
    
    # Test GitHub
    results['GitHub'] = test_github()
    
    # Test Slack
    results['Slack'] = test_slack()
    
    # Test full flow
    if results['GitHub']:
        results['Escalation Flow'] = test_escalation_flow()
    
    # Summary
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)
    
    print(f"\n{passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All integrations working!")
        print("\n💡 The system can now:")
        print("  - Create real GitHub issues from escalations")
        print("  - Send real Slack alerts to your team")
        print("  - No more \"(simulated)\" actions!")
    else:
        print("\n⚠️  Some integrations need configuration.")
        print("    Check the errors above and update your .env file")
