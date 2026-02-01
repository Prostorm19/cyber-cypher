"""
GitHub integration for creating issues and managing escalations.
"""

import os
from typing import Optional, Dict, Any
from github import Github, GithubException
from datetime import datetime


class GitHubClient:
    """
    Client for interacting with GitHub API.
    Creates issues for engineering escalations.
    """
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN', '')
        self.repo_name = os.getenv('GITHUB_REPO', '')
        self.enabled = os.getenv('GITHUB_ENABLED', 'false').lower() == 'true'
        
        self.client = None
        self.repo = None
        
        if self.enabled and self.token and self.repo_name:
            try:
                self.client = Github(self.token)
                self.repo = self.client.get_repo(self.repo_name)
            except Exception as e:
                print(f"Warning: GitHub client initialization failed: {e}")
                self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if GitHub integration is enabled and configured."""
        return self.enabled and self.client is not None and self.repo is not None
    
    def create_issue(
        self,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
        assignees: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue.
        
        Args:
            title: Issue title
            body: Issue body (markdown supported)
            labels: List of label names
            assignees: List of GitHub usernames to assign
        
        Returns:
            Dict with issue details (number, url, etc.)
        """
        if not self.is_enabled():
            return {
                "status": "disabled",
                "message": "GitHub integration is not enabled",
                "simulated": True
            }
        
        try:
            # Create issue
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            
            return {
                "status": "success",
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
                "simulated": False
            }
        except GithubException as e:
            return {
                "status": "error",
                "message": f"GitHub API error: {e.data.get('message', str(e))}",
                "simulated": False
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create issue: {str(e)}",
                "simulated": False
            }
    
    def add_comment(self, issue_number: int, comment: str) -> Dict[str, Any]:
        """Add a comment to an existing issue."""
        if not self.is_enabled():
            return {
                "status": "disabled",
                "message": "GitHub integration is not enabled"
            }
        
        try:
            issue = self.repo.get_issue(issue_number)
            comment_obj = issue.create_comment(comment)
            
            return {
                "status": "success",
                "comment_id": comment_obj.id,
                "comment_url": comment_obj.html_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to add comment: {str(e)}"
            }
    
    def format_escalation_body(
        self,
        hypothesis: str,
        evidence: list[str],
        affected_merchants: list[str],
        potential_causes: list[str],
        confidence: float
    ) -> str:
        """Format escalation details as GitHub issue body."""
        body = f"""## 🚨 Escalation from Support Supervisor

**Hypothesis**: {hypothesis}

**Confidence**: {confidence:.0%}

### 📊 Evidence
"""
        for i, ev in enumerate(evidence, 1):
            body += f"{i}. {ev}\n"
        
        body += "\n### 🔍 Potential Root Causes\n"
        for cause in potential_causes:
            body += f"- {cause}\n"
        
        body += f"\n### 👥 Affected Merchants ({len(affected_merchants)})\n"
        body += ", ".join(f"`{m}`" for m in affected_merchants[:10])
        if len(affected_merchants) > 10:
            body += f"\n...and {len(affected_merchants) - 10} more"
        
        body += f"\n\n### ⏰ Escalated At\n{datetime.utcnow().isoformat()}Z"
        body += "\n\n---\n*This issue was automatically created by the Self-Healing Support Supervisor*"
        
        return body
