from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseProviderAdapter(ABC):
    """Base adapter for different LLM providers."""
    
    @abstractmethod
    def format_messages(self, messages: list) -> list:
        """Format messages for the specific provider."""
        pass
    
    @abstractmethod
    def parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse provider-specific response format."""
        pass