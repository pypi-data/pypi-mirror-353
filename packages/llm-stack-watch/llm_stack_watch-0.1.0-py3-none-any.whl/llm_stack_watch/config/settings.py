import os
from typing import Optional
from dataclasses import dataclass

# Optional: load from .env during development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

@dataclass
class Config:
    """Configuration class for LLM Stack."""
    
    api_key: Optional[str] = None
    logging_url: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3
    enable_logging: bool = True
    
    def __post_init__(self):
        """Load configuration from environment variables if not provided."""
        if self.api_key is None:
            self.api_key = os.environ.get("LLM_STACK_API_KEY")
        
        if self.logging_url is None:
            self.logging_url = os.environ.get("LLM_STACK_LOGGING_URL")
    
    def validate(self) -> bool:
        """Validate configuration."""
        if self.enable_logging and not self.logging_url:
            raise ValueError("Logging URL is required when logging is enabled")
        
        if self.enable_logging and not self.api_key:
            raise ValueError("API key is required when logging is enabled")
        
        return True
