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


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = get_api_key(api_key, provider="gemini")
        if not self.api_key:
            raise APIKeyMissingError(
                "GEMINI_API_KEY is not configured.\n"
                "Run 'git ai settings set-key --provider gemini' or export GEMINI_API_KEY in your shell."
            )

        self.model = get_model(model, provider="gemini")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError as exc:
                raise AIServiceError(
                    "The 'google-genai' package is not installed. Please run: pip install google-genai"
                ) from exc
            except Exception as exc:
                raise AIServiceError(f"Failed to initialize Gemini client: {exc}") from exc
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
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=temperature,
                max_output_tokens=250,
            )
        except ImportError:
            config = {
                "system_instruction": SYSTEM_PROMPT,
                "temperature": temperature,
                "max_output_tokens": 250,
            }

        try:
            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config,
            )
        except Exception as exc:
            err_msg = str(exc).lower()
            if "api_key_invalid" in err_msg or "unauthenticated" in err_msg or "401" in err_msg or "403" in err_msg or "permission denied" in err_msg:
                raise AIAuthenticationError(
                    "Gemini authentication failed. Please verify that your GEMINI_API_KEY is valid."
                ) from exc
            if "resource_exhausted" in err_msg or "429" in err_msg or "quota" in err_msg:
                raise AIServiceError(
                    "Gemini rate limit reached. Please wait a moment and try again."
                ) from exc
            raise AIServiceError(f"Gemini API returned an error: {exc}") from exc

        if not response or not hasattr(response, "text") or not response.text:
            raise AIResponseError("Gemini API returned an empty response. Please try again.")

        cleaned = sanitize_commit_message(response.text)

        if avoid_messages and cleaned in avoid_messages:
            try:
                stronger_prompt = (
                    f"{user_prompt}\n\n"
                    "CRITICAL: The previous message was already generated. You MUST produce a distinct alternative phrasing."
                )
                try:
                    from google.genai import types
                    retry_config = types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.9,
                        max_output_tokens=250,
                    )
                except ImportError:
                    retry_config = {
                        "system_instruction": SYSTEM_PROMPT,
                        "temperature": 0.9,
                        "max_output_tokens": 250,
                    }
                retry_response = client.models.generate_content(
                    model=self.model,
                    contents=stronger_prompt,
                    config=retry_config,
                )
                if retry_response and hasattr(retry_response, "text") and retry_response.text:
                    retry_cleaned = sanitize_commit_message(retry_response.text)
                    if retry_cleaned:
                        return retry_cleaned
            except Exception:
                pass

        if not cleaned:
            raise AIResponseError("Failed to extract a valid commit message from the AI response.")

        return cleaned
