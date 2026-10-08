from __future__ import annotations

from comit.ai.base import (
    ComitAIError,
    APIKeyMissingError,
    AIAuthenticationError,
    AIServiceError,
    AIResponseError,
    UnsupportedProviderError,
    AIProvider,
)
from comit.ai.groq_provider import GroqProvider
from comit.ai.gemini_provider import GeminiProvider
from comit.ai.openai_provider import OpenAIProvider
from comit.ai.ollama_provider import OllamaProvider
from comit.ai.factory import (
    SUPPORTED_PROVIDERS,
    get_provider,
    get_default_provider,
    generate_commit_message,
)

__all__ = [
    "ComitAIError",
    "APIKeyMissingError",
    "AIAuthenticationError",
    "AIServiceError",
    "AIResponseError",
    "UnsupportedProviderError",
    "AIProvider",
    "GroqProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "OllamaProvider",
    "SUPPORTED_PROVIDERS",
    "get_provider",
    "get_default_provider",
    "generate_commit_message",
]
