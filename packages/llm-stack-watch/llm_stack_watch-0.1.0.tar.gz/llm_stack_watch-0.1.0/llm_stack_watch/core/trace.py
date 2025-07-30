import time
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..utils.helpers import generate_id
from .logger import Logger

if TYPE_CHECKING:
    from .base import BaseLLMProvider

class Trace:
    """Traces LLM interactions for monitoring and debugging."""
    
    def __init__(
        self,
        provider: 'BaseLLMProvider',
        user_id: Optional[str] = None,
        label: str = "default",
        meta_data: Optional[Dict[str, Any]] = None
    ):
        self.provider = provider
        self.user_id = user_id
        self.label = label
        self.meta_data = meta_data or {}
        self.trace_id = generate_id()
        self.start_time = time.time()
        self.logger = Logger(provider.config)
    
    def end(self, response: Dict[str, Any], messages: List[Dict[str, str]]) -> bool:
        """End the trace and log the interaction."""
        return self.logger.log(
            provider_name=self.provider.__class__.__name__,
            model=self.provider.model,
            start_time=self.start_time,
            response=response,
            user_message=messages,
            user_id=self.user_id,
            label=self.label,
            meta_data=self.meta_data,
            trace_id=self.trace_id
        )
    
    def add_metadata(self, key: str, value: Any):
        """Add metadata to the trace."""
        self.meta_data[key] = value
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is not None:
            # Log error if exception occurred
            error_response = {
                "error": str(exc_val),
                "error_type": exc_type.__name__
            }
            self.end(error_response, [])
