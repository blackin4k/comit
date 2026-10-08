from __future__ import annotations

from typing import List, Optional

from comit.ai.base import (
    AIProvider,
    APIKeyMissingError,
    AIAuthenticationError,
    AIServiceError,
    AIResponseError,
)
from comit.config import get_api_key, get_model
from comit.prompts import SYSTEM_PROMPT, build_commit_prompt, sanitize_commit_message


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = get_api_key(api_key, provider="openai")
        if not self.api_key:
            raise APIKeyMissingError(
                "OPENAI_API_KEY is not configured.\n"
                "Run 'git ai settings set-key --provider openai' or export OPENAI_API_KEY in your shell."
            )

        self.model = get_model(model, provider="openai")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError as exc:
                raise AIServiceError(
                    "The 'openai' package is not installed. Please run: pip install openai"
                ) from exc
            except Exception as exc:
                raise AIServiceError(f"Failed to initialize OpenAI client: {exc}") from exc
        return self._client

    def generate_commit_message(
        self,
        diff: str,
        recent_commits: Optional[List[str]] = None,
        avoid_messages: Optional[List[str]] = None,
    ) -> str:
        client = self._get_client()
        user_prompt = build_commit_prompt(diff, recent_commits, avoid_messages=avoid_messages)
        temperature = 0.7 if avoid_messages else 0.2

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=250,
            )
        except Exception as exc:
            err_msg = str(exc).lower()
            if "authentication" in err_msg or "incorrect api key" in err_msg or "401" in err_msg or "invalid_api_key" in err_msg:
                raise AIAuthenticationError(
                    "OpenAI authentication failed. Please verify that your OPENAI_API_KEY is valid."
                ) from exc
            if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise AIServiceError(
                    "OpenAI rate limit reached. Please wait a moment and try again."
                ) from exc
            raise AIServiceError(f"OpenAI API returned an error: {exc}") from exc

        if not response or not hasattr(response, "choices") or not response.choices or not response.choices[0].message.content:
            raise AIResponseError("OpenAI API returned an empty response. Please try again.")

        raw_message = response.choices[0].message.content
        cleaned = sanitize_commit_message(raw_message)

        if avoid_messages and cleaned in avoid_messages:
            try:
                stronger_prompt = (
                    f"{user_prompt}\n\n"
                    "CRITICAL: The previous message was already generated. You MUST produce a distinct alternative phrasing."
                )
                retry_response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": stronger_prompt},
                    ],
                    temperature=0.9,
                    max_tokens=250,
                )
                if retry_response and retry_response.choices and retry_response.choices[0].message.content:
                    retry_cleaned = sanitize_commit_message(retry_response.choices[0].message.content)
                    if retry_cleaned:
                        return retry_cleaned
            except Exception:
                pass

        if not cleaned:
            raise AIResponseError("Failed to extract a valid commit message from the AI response.")

        return cleaned
