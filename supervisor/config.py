"""Configuration management for the supervisor system."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-2.0-flash-exp"
    llm_enabled: bool = False
    
    # GitHub Integration
    github_token: str = ""
    github_repo: str = ""
    github_enabled: bool = False
    
    # Slack Integration
    slack_webhook_url: str = ""
    slack_enabled: bool = False
    
    # Database
    database_url: str = "sqlite:///./supervisor.db"
    
    # Agent Configuration
    confidence_threshold: float = 0.75
    auto_approve_low_risk: bool = True
    max_short_term_memory_days: int = 7
    
    # Pattern Detection
    min_pattern_frequency: int = 2  # Minimum occurrences to consider a pattern
    pattern_time_window_hours: int = 24  # Time window for pattern detection
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", "supervisor.log")
    
    class Config:
        env_file = ".env"


settings = Settings()
