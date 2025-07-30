import uuid
import time
from datetime import datetime
from typing import Any, Dict

def generate_id() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())

def get_timestamp() -> float:
    """Get current timestamp."""
    return time.time()

def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize sensitive data before logging."""
    sensitive_keys = ['api_key', 'token', 'password', 'secret']
    sanitized = data.copy()
    
    for key in sensitive_keys:
        if key in sanitized:
            sanitized[key] = "***REDACTED***"
    
    return sanitized