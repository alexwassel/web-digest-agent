
import os
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient

def get_model_client(provider: str, model_name: str):
    provider = provider.lower()
    if provider == 'openai':
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            raise RuntimeError('OPENAI_API_KEY not set')
        return OpenAIClient(api_key=key, model=model_name)
    elif provider == 'anthropic':
        key = os.getenv('ANTHROPIC_API_KEY')
        if not key:
            raise RuntimeError('ANTHROPIC_API_KEY not set')
        return AnthropicClient(api_key=key, model=model_name)
    else:
        raise ValueError(f'Unknown provider: {provider}')
