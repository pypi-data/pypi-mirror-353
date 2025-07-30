import anthropic
from typing import List, Dict, Any, Optional
from ..core.base import BaseLLMProvider
from ..config.settings import Config
from ..utils.exceptions import ProviderError

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, model: str, config: Config, api_key: Optional[str]):
        super().__init__(model, config)
        self.client = anthropic.Anthropic(api_key=api_key)
    
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
                messages=formatted_messages,
                system=system_message,
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
