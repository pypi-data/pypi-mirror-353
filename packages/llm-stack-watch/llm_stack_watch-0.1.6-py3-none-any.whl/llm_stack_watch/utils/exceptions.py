class LLMStackError(Exception):
    """Base exception for LLM Stack library."""
    def __init__(self, message: str = "An error occurred in the LLM Stack library"):
        super().__init__(message)


class ConfigurationError(LLMStackError):
    """Raised when configuration is invalid."""
    def __init__(self, message: str = "Invalid configuration detected"):
        super().__init__(message)


class LoggingError(LLMStackError):
    """Raised when logging operations fail."""
    def __init__(self, message: str = "Logging operation failed"):
        super().__init__(message)


class ProviderError(LLMStackError):
    """Raised when provider operations fail."""
    def __init__(self, message: str = "Provider operation failed"):
        super().__init__(message)
