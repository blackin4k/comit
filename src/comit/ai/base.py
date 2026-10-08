from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional


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


class UnsupportedProviderError(ComitAIError):
    pass


class AIProvider(ABC):
    @abstractmethod
    def generate_commit_message(
        self,
        diff: str,
        recent_commits: Optional[List[str]] = None,
        avoid_messages: Optional[List[str]] = None,
    ) -> str:
        pass
