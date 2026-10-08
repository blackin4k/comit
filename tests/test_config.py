import json
import os
from pathlib import Path
from unittest.mock import patch
import pytest

from comit.config import (
    get_config_dir,
    get_config_path,
    load_user_config,
    save_user_config,
    set_user_config_value,
    reset_user_config,
    get_api_key,
    get_model,
    get_provider,
    mask_api_key,
    normalize_api_key,
    get_config_summary,
    DEFAULT_GROQ_MODEL,
    DEFAULT_PROVIDER,
)


@pytest.fixture
def temp_config_dir(tmp_path: Path, monkeypatch):
    custom_dir = tmp_path / "comit_config"
    monkeypatch.setattr("comit.config.get_config_dir", lambda: custom_dir)
    return custom_dir


def test_mask_api_key():
    assert mask_api_key(None) == "Not configured"
    assert mask_api_key("") == "Not configured"
    assert mask_api_key("1234") == "****"
    assert mask_api_key("gsk_1234567890abcdef") == "gsk_************cdef"


def test_save_and_load_user_config(temp_config_dir: Path):
    assert load_user_config() == {}
    save_user_config({"groq_api_key": "gsk_test123", "groq_model": "custom-model"})
    loaded = load_user_config()
    assert loaded["groq_api_key"] == "gsk_test123"
    assert loaded["groq_model"] == "custom-model"


def test_set_user_config_value(temp_config_dir: Path):
    set_user_config_value("groq_model", "test-model-1")
    assert load_user_config().get("groq_model") == "test-model-1"


def test_reset_user_config(temp_config_dir: Path):
    set_user_config_value("groq_model", "test-model")
    assert (temp_config_dir / "config.json").is_file()
    reset_user_config()
    assert not (temp_config_dir / "config.json").is_file()
    assert load_user_config() == {}


def test_config_precedence_api_key(temp_config_dir: Path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)

    # 1. No env and no config
    assert get_api_key() is None

    # 2. User config set
    set_user_config_value("groq_api_key", "gsk_user_config_key")
    assert get_api_key() == "gsk_user_config_key"

    # 3. Environment variable overrides user config
    monkeypatch.setenv("GROQ_API_KEY", "gsk_env_key")
    assert get_api_key() == "gsk_env_key"

    # 4. Explicit override takes absolute precedence
    assert get_api_key("gsk_override_key") == "gsk_override_key"


def test_config_precedence_model(temp_config_dir: Path, monkeypatch):
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.delenv("groq_model", raising=False)

    # 1. Default model
    assert get_model() == DEFAULT_GROQ_MODEL

    # 2. User config model
    set_user_config_value("groq_model", "model-from-user-config")
    assert get_model() == "model-from-user-config"

    # 3. Environment variable overrides user config
    monkeypatch.setenv("GROQ_MODEL", "model-from-env")
    assert get_model() == "model-from-env"

    # 4. Explicit override takes absolute precedence
    assert get_model("model-override") == "model-override"


def test_get_provider_default(temp_config_dir: Path, monkeypatch):
    monkeypatch.delenv("COMIT_PROVIDER", raising=False)
    assert get_provider() == DEFAULT_PROVIDER

    set_user_config_value("provider", "custom_provider")
    assert get_provider() == "custom_provider"

    monkeypatch.setenv("COMIT_PROVIDER", "env_provider")
    assert get_provider() == "env_provider"


def test_normalize_api_key():
    assert normalize_api_key(None) is None
    assert normalize_api_key("") is None
    assert normalize_api_key("   ") is None
    assert normalize_api_key("gsk_abc123") == "gsk_abc123"
    assert normalize_api_key('"gsk_abc123"') == "gsk_abc123"
    assert normalize_api_key("'gsk_abc123'") == "gsk_abc123"
    assert normalize_api_key('  "gsk_abc123"  ') == "gsk_abc123"
    assert normalize_api_key("  'gsk_abc123'  ") == "gsk_abc123"
    assert normalize_api_key('  "  gsk_abc123  "  ') == "gsk_abc123"
    assert normalize_api_key('gsk_"inner"_123') == 'gsk_"inner"_123'


def test_mask_api_key_with_quotes():
    assert mask_api_key('"gsk_1234567890abcdef"') == "gsk_************cdef"
    assert mask_api_key("'gsk_1234567890abcdef'") == "gsk_************cdef"
    assert mask_api_key('  "gsk_1234567890abcdef"  ') == "gsk_************cdef"


def test_get_api_key_with_existing_incorrectly_quoted_config(temp_config_dir: Path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    monkeypatch.delenv("Groq_Api_Key", raising=False)
    monkeypatch.delenv("GROQ_KEY", raising=False)

    save_user_config({"groq_api_key": '"gsk_already_quoted_1234567890"'})
    assert get_api_key() == "gsk_already_quoted_1234567890"

def test_get_config_summary(temp_config_dir: Path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("groq_api_key", raising=False)
    set_user_config_value("groq_api_key", "gsk_1234567890abcdef")
    set_user_config_value("groq_model", "test-model")

    summary = get_config_summary()
    assert summary["model"] == "test-model"
    assert summary["api_key_masked"] == "gsk_************cdef"
    assert summary["config_exists"] is True


