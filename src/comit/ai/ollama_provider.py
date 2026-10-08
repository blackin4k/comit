from __future__ import annotations

from typing import List, Optional, Union

from comit.ai.base import (
    AIProvider,
    AIServiceError,
    AIResponseError,
)
from comit.commit.context import CommitContext
from comit.config import get_model, get_ollama_host
from comit.prompts import SYSTEM_PROMPT, build_commit_prompt, sanitize_commit_message


class OllamaProvider(AIProvider):
    def __init__(self, model: Optional[str] = None, host: Optional[str] = None):
        self.model = get_model(model, provider="ollama")
        self.host = get_ollama_host(host)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.host)
            except ImportError as exc:
                raise AIServiceError(
                    "The 'ollama' package is not installed. Please run: pip install ollama"
                ) from exc
            except Exception as exc:
                raise AIServiceError(f"Failed to initialize Ollama client: {exc}") from exc
        return self._client

    def generate_commit_message(
        self,
        context: Union[CommitContext, str, None] = None,
        recent_commits: Optional[List[str]] = None,
        avoid_messages: Optional[List[str]] = None,
        diff: Optional[str] = None,
    ) -> str:
        target = context if context is not None else (diff or "")
        client = self._get_client()
        user_prompt = build_commit_prompt(target, recent_commits=recent_commits, avoid_messages=avoid_messages)
        temperature = 0.7 if avoid_messages else 0.2

        try:
            response = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": temperature, "num_predict": 250},
            )
        except Exception as exc:
            err_msg = str(exc)
            if "ConnectError" in err_msg or "ConnectionRefused" in err_msg or "connection refused" in err_msg.lower() or "Failed to connect" in err_msg:
                raise AIServiceError(
                    f"Could not connect to Ollama server at {self.host}. Please ensure the Ollama service is running."
                ) from exc
            if "not found" in err_msg.lower() and "model" in err_msg.lower():
                raise AIServiceError(
                    f"Ollama model '{self.model}' was not found. Please run 'ollama pull {self.model}' first."
                ) from exc
            raise AIServiceError(f"Ollama error: {exc}") from exc

        content = ""
        if isinstance(response, dict):
            content = response.get("message", {}).get("content", "")
        elif hasattr(response, "message") and hasattr(response.message, "content"):
            content = response.message.content

        if not content:
            raise AIResponseError("Ollama returned an empty response. Please try again.")

        cleaned = sanitize_commit_message(content)

        if avoid_messages and cleaned in avoid_messages:
            try:
                stronger_prompt = (
                    f"{user_prompt}\n\n"
                    "CRITICAL: The previous message was already generated. You MUST produce a distinct alternative phrasing."
                )
                retry_response = client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": stronger_prompt},
                    ],
                    options={"temperature": 0.9, "num_predict": 250},
                )
                retry_content = ""
                if isinstance(retry_response, dict):
                    retry_content = retry_response.get("message", {}).get("content", "")
                elif hasattr(retry_response, "message") and hasattr(retry_response.message, "content"):
                    retry_content = retry_response.message.content
                if retry_content:
                    retry_cleaned = sanitize_commit_message(retry_content)
                    if retry_cleaned:
                        return retry_cleaned
            except Exception:
                pass

        if not cleaned:
            raise AIResponseError("Failed to extract a valid commit message from the AI response.")

        return cleaned
