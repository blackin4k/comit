from __future__ import annotations

from typing import List, Optional

from comit.ai.base import (
    AIProvider,
    UnsupportedProviderError,
)
from comit.ai.groq_provider import GroqProvider
from comit.ai.gemini_provider import GeminiProvider
from comit.ai.openai_provider import OpenAIProvider
from comit.ai.ollama_provider import OllamaProvider
from comit.config import get_provider as config_get_provider

SUPPORTED_PROVIDERS = ("groq", "gemini", "openai", "ollama")


def get_provider(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> AIProvider:
    name = (provider_name or config_get_provider()).strip().lower()

    if name == "groq":
        return GroqProvider(api_key=api_key, model=model)
    elif name == "gemini":
        return GeminiProvider(api_key=api_key, model=model)
    elif name == "openai":
        return OpenAIProvider(api_key=api_key, model=model)
    elif name == "ollama":
        return OllamaProvider(model=model)
    else:
        supported_str = ", ".join(SUPPORTED_PROVIDERS)
        raise UnsupportedProviderError(
            f"Unsupported AI provider '{name}'. Supported providers: {supported_str}"
        )


def get_default_provider() -> AIProvider:
    return get_provider()


def generate_commit_message(
    diff: str,
    recent_commits: Optional[List[str]] = None,
    avoid_messages: Optional[List[str]] = None,
    provider: Optional[AIProvider] = None,
) -> str:
    if provider is None:
        provider = get_default_provider()
    return provider.generate_commit_message(
        diff=diff, recent_commits=recent_commits, avoid_messages=avoid_messages
    )
