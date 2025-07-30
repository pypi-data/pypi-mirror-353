import pytest
import os
from llm_stack.config.settings import Config
from llm_stack.utils.exceptions import ConfigurationError

class TestConfig:
    
    def test_config_initialization(self):
        """Test basic config initialization."""
        config = Config(
            api_key="test-key",
            logging_url="https://test.com"
        )
        assert config.api_key == "test-key"
        assert config.logging_url == "https://test.com"
        assert config.timeout == 30
        assert config.enable_logging is True
    
    def test_config_from_env(self, monkeypatch):
        """Test config loading from environment variables."""
        monkeypatch.setenv("LLM_STACK_API_KEY", "env-key") 
        monkeypatch.setenv("LLM_STACK_LOGGING_URL", "https://env.com")
        
        config = Config()
        assert config.api_key == "env-key"
        assert config.logging_url == "https://env.com"
    
    def test_config_validation_success(self):
        """Test successful config validation."""
        config = Config(
            api_key="test-key",
            logging_url="https://test.com",
            enable_logging=True
        )
        assert config.validate() is True
    
    def test_config_validation_missing_url(self):
        """Test error config validation"""
        
        """Test successful config validation."""
        config = Config(
            enable_logging=True
        )
        assert config.validate() is False