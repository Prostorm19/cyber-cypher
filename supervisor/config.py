"""Configuration management for the supervisor system."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./supervisor.db")
    
    # Agent Configuration
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    auto_approve_low_risk: bool = os.getenv("AUTO_APPROVE_LOW_RISK", "true").lower() == "true"
    max_short_term_memory_days: int = int(os.getenv("MAX_SHORT_TERM_MEMORY_DAYS", "7"))
    
    # Pattern Detection
    min_pattern_frequency: int = 2  # Minimum occurrences to consider a pattern
    pattern_time_window_hours: int = 24  # Time window for pattern detection
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", "supervisor.log")
    
    class Config:
        env_file = ".env"


settings = Settings()
