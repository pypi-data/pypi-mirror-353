import pytest
from llm_stack.config.settings import Config

@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    return Config(
        api_key="test-api-key",
        logging_url="https://test-endpoint.com/logs",
        timeout=10,
        retry_attempts=1,
        enable_logging=True
    )

@pytest.fixture
def mock_messages():
    """Provide mock messages for testing."""
    return [
        {"role": "user", "content": "Hello, how are you?"}
    ]

@pytest.fixture
def mock_response():
    """Provide a mock LLM response for testing."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "I'm doing well, thank you!"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 8,
            "total_tokens": 18
        }
    }