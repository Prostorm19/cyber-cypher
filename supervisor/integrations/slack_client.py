"""
Slack integration for sending alerts and notifications.
"""

import os
import json
from typing import Dict, Any, Optional
import requests
from datetime import datetime


class SlackClient:
    """
    Client for sending messages to Slack via webhooks.
    """
    
    def __init__(self):
        self.webhook_url = os.getenv('SLACK_WEBHOOK_URL', '')
        self.enabled = os.getenv('SLACK_ENABLED', 'false').lower() == 'true'
    
    def is_enabled(self) -> bool:
        """Check if Slack integration is enabled and configured."""
        return self.enabled and bool(self.webhook_url)
    
    def send_message(
        self,
        text: str,
        blocks: Optional[list] = None,
        username: str = "Support Supervisor",
        icon_emoji: str = ":robot_face:"
    ) -> Dict[str, Any]:
        """
        Send a message to Slack.
        
        Args:
            text: Plain text message (fallback)
            blocks: Slack Block Kit blocks for rich formatting
            username: Bot username to display
            icon_emoji: Emoji icon for the bot
        
        Returns:
            Dict with status and response details
        """
        if not self.is_enabled():
            return {
                "status": "disabled",
                "message": "Slack integration is not enabled",
                "simulated": True
            }
        
        try:
            payload = {
                "text": text,
                "username": username,
                "icon_emoji": icon_emoji
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200 and response.text == "ok":
                return {
                    "status": "success",
                    "message": "Message sent to Slack",
                    "simulated": False
                }
            else:
                return {
                    "status": "error",
                    "message": f"Slack API error: {response.text}",
                    "status_code": response.status_code,
                    "simulated": False
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to send Slack message: {str(e)}",
                "simulated": False
            }
    
    def send_alert(
        self,
        priority: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a formatted alert to Slack.
        
        Args:
            priority: Alert priority (low/medium/high)
            message: Alert message
            details: Additional details to include
        
        Returns:
            Dict with status and response details
        """
        # Determine emoji and color based on priority
        emoji_map = {
            "low": ":information_source:",
            "medium": ":warning:",
            "high": ":rotating_light:"
        }
        color_map = {
            "low": "#36a64f",  # Green
            "medium": "#ff9900",  # Orange
            "high": "#ff0000"  # Red
        }
        
        emoji = emoji_map.get(priority.lower(), ":bell:")
        color = color_map.get(priority.lower(), "#439FE0")
        
        # Build Slack blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Support Supervisor Alert",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{priority.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Message:*\n{message}"
                }
            }
        ]
        
        # Add details if provided
        if details:
            detail_text = "\n".join([f"• *{k}:* {v}" for k, v in details.items()])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{detail_text}"
                }
            })
        
        blocks.append({"type": "divider"})
        
        # Send message
        return self.send_message(
            text=f"[{priority.upper()}] {message}",
            blocks=blocks
        )
    
    def send_escalation_notification(
        self,
        hypothesis: str,
        confidence: float,
        affected_merchants_count: int,
        github_issue_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification about engineering escalation."""
        message = f"Engineering escalation created: {hypothesis}"
        
        details = {
            "Confidence": f"{confidence:.0%}",
            "Affected Merchants": str(affected_merchants_count)
        }
        
        if github_issue_url:
            details["GitHub Issue"] = github_issue_url
        
        return self.send_alert("high", message, details)
