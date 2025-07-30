import anthropic
import os
from typing import List, Dict, Any, Optional
from llm_stack_watch.core.base import BaseLLMProvider
from llm_stack_watch.config.settings import Config
from llm_stack_watch.utils.exceptions import ProviderError

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, model: str, config: Config, api_key: Optional[str] = None):
        super().__init__(model, config)
        
        # Get API key from parameter, config, or environment
        self.anthropic_api_key = (
            api_key or 
            config.anthropic_api_key or 
            os.environ.get("ANTHROPIC_API_KEY")
        )
        
        if not self.anthropic_api_key:
            raise ProviderError(
                "Anthropic API key is required. Provide it via:\n"
                "1. api_key parameter\n"
                "2. config.anthropic_api_key\n" 
                "3. ANTHROPIC_API_KEY environment variable"
            )
        
        self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to Anthropic."""
        try:
            # Convert OpenAI format to Anthropic format
            system_message = None
            formatted_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    formatted_messages.append(msg)
            
            response = self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() if k != "max_tokens"}
            )
            
            # Convert to OpenAI-like format for consistency
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": response.content[0].text
                    }
                }],
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            raise ProviderError(f"Anthropic API error: {str(e)}")
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """Stream chat completion from Anthropic."""
        # Implementation for streaming
        raise NotImplementedError("Anthropic streaming not yet implemented")