from unittest.mock import MagicMock, patch
import pytest

from comit.ai import (
    AIProvider,
    GroqProvider,
    GeminiProvider,
    OpenAIProvider,
    OllamaProvider,
    get_provider,
    get_default_provider,
    APIKeyMissingError,
    AIAuthenticationError,
    AIServiceError,
    AIResponseError,
    UnsupportedProviderError,
    generate_commit_message,
)


def test_factory_get_provider():
    groq_p = get_provider("groq", api_key="mock_key")
    assert isinstance(groq_p, GroqProvider)

    gemini_p = get_provider("gemini", api_key="mock_key")
    assert isinstance(gemini_p, GeminiProvider)

    openai_p = get_provider("openai", api_key="mock_key")
    assert isinstance(openai_p, OpenAIProvider)

    ollama_p = get_provider("ollama")
    assert isinstance(ollama_p, OllamaProvider)


def test_factory_unsupported_provider():
    with pytest.raises(UnsupportedProviderError) as exc_info:
        get_provider("unsupported_ai")
    assert "Unsupported AI provider" in str(exc_info.value)
    assert "groq" in str(exc_info.value)


def test_groq_provider_missing_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)
    with patch("comit.config.get_api_key", return_value=None):
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


def test_groq_provider_regeneration_with_avoid():
    mock_choice = MagicMock()
    mock_choice.message.content = "feat: add theme customizer"
    mock_response = MagicMock(choices=[mock_choice])

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = GroqProvider(api_key="mock_key")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff...",
        recent_commits=["feat: init"],
        avoid_messages=["feat: support custom themes"],
    )

    assert result == "feat: add theme customizer"
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args["temperature"] == 0.7
    user_msg = [m["content"] for m in call_args["messages"] if m["role"] == "user"][0]
    assert "feat: support custom themes" in user_msg


def test_groq_provider_regeneration_retry_duplicate():
    mock_dup = MagicMock()
    mock_dup.message.content = "feat: duplicate msg"
    mock_dup_resp = MagicMock(choices=[mock_dup])

    mock_retry = MagicMock()
    mock_retry.message.content = "feat: new distinct alternative"
    mock_retry_resp = MagicMock(choices=[mock_retry])

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [mock_dup_resp, mock_retry_resp]

    provider = GroqProvider(api_key="mock_key")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff...",
        recent_commits=["feat: init"],
        avoid_messages=["feat: duplicate msg"],
    )

    assert result == "feat: new distinct alternative"
    assert mock_client.chat.completions.create.call_count == 2


def test_groq_provider_empty_response():
    mock_response = MagicMock(choices=[])
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = GroqProvider(api_key="mock_key")
    provider._client = mock_client

    with pytest.raises(AIResponseError):
        provider.generate_commit_message(diff="diff...", recent_commits=[])


def test_gemini_provider_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("gemini_api_key", raising=False)
    with patch("comit.config.get_api_key", return_value=None):
        with pytest.raises(APIKeyMissingError) as exc_info:
            GeminiProvider(api_key="")
        assert "GEMINI_API_KEY" in str(exc_info.value)


def test_gemini_provider_success():
    mock_response = MagicMock()
    mock_response.text = "feat: add gemini provider"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    provider = GeminiProvider(api_key="mock_gemini_key")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff --git a/app.py...",
        recent_commits=["feat: init"],
    )

    assert result == "feat: add gemini provider"
    mock_client.models.generate_content.assert_called_once()


def test_gemini_provider_empty_response():
    mock_response = MagicMock()
    mock_response.text = ""

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    provider = GeminiProvider(api_key="mock_gemini_key")
    provider._client = mock_client

    with pytest.raises(AIResponseError):
        provider.generate_commit_message(diff="diff...", recent_commits=[])


def test_openai_provider_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("openai_api_key", raising=False)
    with patch("comit.config.get_api_key", return_value=None):
        with pytest.raises(APIKeyMissingError) as exc_info:
            OpenAIProvider(api_key="")
        assert "OPENAI_API_KEY" in str(exc_info.value)


def test_openai_provider_success():
    mock_choice = MagicMock()
    mock_choice.message.content = "feat: add openai provider"
    mock_response = MagicMock(choices=[mock_choice])

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    provider = OpenAIProvider(api_key="mock_openai_key")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff --git a/app.py...",
        recent_commits=["feat: init"],
    )

    assert result == "feat: add openai provider"
    mock_client.chat.completions.create.assert_called_once()


def test_ollama_provider_no_api_key_required():
    provider = OllamaProvider(model="llama3.2")
    assert provider.model == "llama3.2"
    assert "localhost" in provider.host or "127.0.0.1" in provider.host


def test_ollama_provider_success():
    mock_client = MagicMock()
    mock_client.chat.return_value = {
        "message": {"content": "feat: add ollama local inference"}
    }

    provider = OllamaProvider(model="llama3.2")
    provider._client = mock_client

    result = provider.generate_commit_message(
        diff="diff --git a/app.py...",
        recent_commits=["feat: init"],
    )

    assert result == "feat: add ollama local inference"
    mock_client.chat.assert_called_once()


def test_ollama_provider_connection_error():
    mock_client = MagicMock()
    mock_client.chat.side_effect = Exception("Failed to connect to host: ConnectionRefusedError")

    provider = OllamaProvider(model="llama3.2")
    provider._client = mock_client

    with pytest.raises(AIServiceError) as exc_info:
        provider.generate_commit_message(diff="diff...", recent_commits=[])
    assert "Could not connect to Ollama server" in str(exc_info.value)


def test_generate_commit_message_with_custom_provider():
    class DummyProvider(AIProvider):
        def generate_commit_message(self, diff, recent_commits=None, avoid_messages=None):
            return "refactor: simplify test setup"

    msg = generate_commit_message("diff...", provider=DummyProvider())
    assert msg == "refactor: simplify test setup"
