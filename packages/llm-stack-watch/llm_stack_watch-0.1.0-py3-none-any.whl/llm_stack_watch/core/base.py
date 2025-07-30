from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..config.settings import Config
from utils.helpers import generate_id

class BaseLLMProvider(ABC):
    """Base class for all LLM providers."""
    
    def __init__(self, model: str, config: Config):
        self.model = model
        self.config = config
        self.conversation_id = generate_id()
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to the LLM provider."""
        pass
    
    @abstractmethod
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """Stream chat completion from the LLM provider."""
        pass
    
    def trace(
        self, 
        user_id: Optional[str] = None,
        label: str = "default",
        meta_data: Optional[Dict[str, Any]] = None
    ) -> 'Trace':
        """Create a trace for this provider."""
        from .trace import Trace
        return Trace(
            provider=self,
            user_id=user_id,
            label=label,
            meta_data=meta_data
        )
