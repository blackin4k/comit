from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from comit.config import get_api_key, get_model
from comit.prompts import SYSTEM_PROMPT, build_commit_prompt, sanitize_commit_message


class ComitAIError(Exception):
    pass


class APIKeyMissingError(ComitAIError):
    pass


class AIAuthenticationError(ComitAIError):
    pass


class AIServiceError(ComitAIError):
    pass


class AIResponseError(ComitAIError):
    pass


class AIProvider(ABC):
    @abstractmethod
    def generate_commit_message(
        self, diff: str, recent_commits: Optional[List[str]] = None
    ) -> str:
        pass


class GroqProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = get_api_key(api_key)
        if not self.api_key:
            raise APIKeyMissingError(
                "GROQ_API_KEY is not configured.\n"
                "Run 'git ai settings' to set your API key or export GROQ_API_KEY in your shell."
            )

        self.model = get_model(model)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError as exc:
                raise AIServiceError(
                    "The 'groq' package is not installed. Please run: pip install groq"
                ) from exc
            except Exception as exc:
                raise AIServiceError(f"Failed to initialize Groq client: {exc}") from exc
        return self._client

    def generate_commit_message(
        self, diff: str, recent_commits: Optional[List[str]] = None
    ) -> str:
        import groq

        client = self._get_client()
        user_prompt = build_commit_prompt(diff, recent_commits)

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=250,
            )
        except groq.AuthenticationError as exc:
            raise AIAuthenticationError(
                "Groq authentication failed. Please verify that your GROQ_API_KEY is valid."
            ) from exc
        except groq.RateLimitError as exc:
            raise AIServiceError(
                "Groq rate limit reached. Please wait a moment and try again."
            ) from exc
        except groq.APIConnectionError as exc:
            raise AIServiceError(
                "Could not connect to the Groq API. Please check your internet connection."
            ) from exc
        except groq.APIStatusError as exc:
            raise AIServiceError(
                f"Groq API returned an error (status {exc.status_code}): {exc.message}"
            ) from exc
        except Exception as exc:
            raise AIServiceError(f"Unexpected error while calling Groq API: {exc}") from exc

        if not response.choices or not response.choices[0].message.content:
            raise AIResponseError("Groq API returned an empty response. Please try again.")

        raw_message = response.choices[0].message.content
        cleaned = sanitize_commit_message(raw_message)

        if not cleaned:
            raise AIResponseError("Failed to extract a valid commit message from the AI response.")

        return cleaned


def get_default_provider() -> AIProvider:
    return GroqProvider()


def generate_commit_message(
    diff: str,
    recent_commits: Optional[List[str]] = None,
    provider: Optional[AIProvider] = None,
) -> str:
    if provider is None:
        provider = get_default_provider()
    return provider.generate_commit_message(diff, recent_commits)
