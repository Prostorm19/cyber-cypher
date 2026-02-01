"""
Integrations package for external services.
"""

from supervisor.integrations.github_client import GitHubClient
from supervisor.integrations.slack_client import SlackClient

__all__ = ['GitHubClient', 'SlackClient']
