import openai
from typing import List, Dict, Any, Optional
from ..core.base import BaseLLMProvider
from ..config.settings import Config
from ..utils.exceptions import ProviderError

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, model: str, config: Config, api_key: Optional[str]):
        super().__init__(model, config)
        self.client = openai.OpenAI(api_key=api_key)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Send chat completion request to OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.model_dump()
        except Exception as e:
            raise ProviderError(f"OpenAI API error: {str(e)}")
    
    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """Stream chat completion from OpenAI."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            for chunk in stream:
                yield chunk.model_dump()
        except Exception as e:
            raise ProviderError(f"OpenAI streaming error: {str(e)}")
