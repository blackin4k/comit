from unittest.mock import MagicMock, patch
import pytest

from comit.ai import (
    GroqProvider,
    APIKeyMissingError,
    AIAuthenticationError,
    AIServiceError,
    AIResponseError,
    generate_commit_message,
)


def test_groq_provider_missing_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    with patch("comit.ai.get_api_key", return_value=None):
        with pytest.raises(APIKeyMissingError) as exc_info:
            GroqProvider(api_key="")
        assert "GROQ_API_KEY" in str(exc_info.value)


def test_groq_provider_success():
    mock_choice = MagicMock()
    mock_choice.message.content = "feat: support custom themes"
    mock_response = MagicMock(choices=[mock_choice])

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = GroqProvider(api_key="mock_key")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff --git a/theme.css...",
        recent_commits=["feat: initial setup"],
    )

    assert result == "feat: support custom themes"
    mock_client.chat.completions.create.assert_called_once()


def test_groq_provider_empty_response():
    mock_response = MagicMock(choices=[])
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = GroqProvider(api_key="mock_key")
    provider._client = mock_client

    with pytest.raises(AIResponseError):
        provider.generate_commit_message(diff="diff...", recent_commits=[])


def test_generate_commit_message_with_custom_provider():
    class DummyProvider:
        def generate_commit_message(self, diff, recent_commits=None):
            return "refactor: simplify test setup"

    msg = generate_commit_message("diff...", provider=DummyProvider())
    assert msg == "refactor: simplify test setup"
