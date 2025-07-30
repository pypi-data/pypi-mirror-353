import requests
import time
from typing import Dict, Any, Optional, List
from ..config.settings import Config
from ..utils.exceptions import LoggingError
from ..utils.helpers import sanitize_data

class Logger:
    """Handles logging of LLM interactions."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def log(
        self, 
        provider_name: str,
        model: str, 
        start_time: float, 
        response: Dict[str, Any],
        user_message: List[Dict[str, str]],
        user_id: Optional[str] = None,
        label: str = "default",
        meta_data: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ) -> bool:
        """Log LLM interaction data."""
        
        if not self.config.enable_logging:
            return True
            
        duration = time.time() - start_time
        usage = response.get("usage", {})
        choices = response.get("choices", [{}])
        
        payload = {
            "trace_id": trace_id,
            "provider": provider_name,
            "model": model,
            "duration": duration,
            "timestamp": start_time,
            "user_id": user_id,
            "label": label,
            "meta_data": meta_data or {},
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "assistant_message": choices[0].get("message", {}),
            "user_message": user_message,
            "status": "success" if response else "error"
        }
        
        # Sanitize sensitive data
        payload = sanitize_data(payload)
        
        return self._send_log(payload)
    
    def _send_log(self, payload: Dict[str, Any]) -> bool:
        """Send log data to the logging endpoint."""
        for attempt in range(self.config.retry_attempts):
            try:
                response = requests.post(
                    url=self.config.logging_url,
                    json=payload,
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                return True
                
            except requests.RequestException as e:
                if attempt == self.config.retry_attempts - 1:
                    print(f"[LLM-STACK] Logging failed after {self.config.retry_attempts} attempts: {e}")
                    return False
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return False