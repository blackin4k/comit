from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

DEFAULT_PROVIDER = "groq"
DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OLLAMA_MODEL = "llama3.2"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"

DEFAULT_MODELS = {
    "groq": DEFAULT_GROQ_MODEL,
    "gemini": DEFAULT_GEMINI_MODEL,
    "openai": DEFAULT_OPENAI_MODEL,
    "ollama": DEFAULT_OLLAMA_MODEL,
}

SUPPORTED_PROVIDERS = ("groq", "gemini", "openai", "ollama")


def get_config_dir() -> Path:
    if sys.platform == "win32":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "comit"
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "comit"
    return Path.home() / ".config" / "comit"


def get_config_path() -> Path:
    return get_config_dir() / "config.json"


def load_user_config() -> Dict[str, Any]:
    config_file = get_config_path()
    if not config_file.is_file():
        return {}
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_user_config(data: Dict[str, Any]) -> None:
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = get_config_path()
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def set_user_config_value(key: str, value: Any) -> None:
    data = load_user_config()
    data[key] = value
    save_user_config(data)


def reset_user_config() -> None:
    config_file = get_config_path()
    if config_file.is_file():
        config_file.unlink()


def normalize_api_key(key: Optional[str]) -> Optional[str]:
    if not key:
        return None
    val = str(key).strip()
    if not val:
        return None
    while (len(val) >= 2) and (
        (val.startswith('"') and val.endswith('"')) or
        (val.startswith("'") and val.endswith("'"))
    ):
        val = val[1:-1].strip()
    return val if val else None


def get_provider(override_provider: Optional[str] = None) -> str:
    if override_provider and override_provider.strip():
        return override_provider.strip().lower()

    for var in ("COMIT_PROVIDER", "comit_provider"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip().lower()

    user_cfg = load_user_config()
    cfg_val = user_cfg.get("provider")
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip().lower()

    return DEFAULT_PROVIDER


def get_api_key(
    override_key: Optional[str] = None,
    provider: Optional[str] = None,
) -> Optional[str]:
    p = (provider or get_provider()).strip().lower()

    if override_key:
        normalized = normalize_api_key(override_key)
        if normalized:
            return normalized

    if p == "ollama":
        return None

    env_vars_map = {
        "groq": ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"),
        "gemini": ("GEMINI_API_KEY", "gemini_api_key", "Gemini_Api_Key"),
        "openai": ("OPENAI_API_KEY", "openai_api_key", "Openai_Api_Key"),
    }
    vars_to_check = env_vars_map.get(p, (f"{p.upper()}_API_KEY",))

    for var in vars_to_check:
        val = os.getenv(var)
        if val:
            normalized = normalize_api_key(val)
            if normalized:
                return normalized

    for k, v in os.environ.items():
        if k.strip().lower() in [var.lower() for var in vars_to_check] and v:
            normalized = normalize_api_key(v)
            if normalized:
                return normalized

    user_cfg = load_user_config()
    cfg_keys = [f"{p}_api_key", f"{p}_key"]
    if p == "groq":
        cfg_keys.extend(["groq_api_key", "api_key"])
    for key in cfg_keys:
        cfg_val = user_cfg.get(key)
        if cfg_val:
            normalized = normalize_api_key(cfg_val)
            if normalized:
                return normalized

    return None


def get_model(
    override_model: Optional[str] = None,
    provider: Optional[str] = None,
) -> str:
    p = (provider or get_provider()).strip().lower()

    if override_model and override_model.strip():
        return override_model.strip()

    for var in ("COMIT_MODEL", "comit_model"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    env_vars_map = {
        "groq": ("GROQ_MODEL", "groq_model", "Groq_Model"),
        "gemini": ("GEMINI_MODEL", "gemini_model", "Gemini_Model"),
        "openai": ("OPENAI_MODEL", "openai_model", "Openai_Model"),
        "ollama": ("OLLAMA_MODEL", "ollama_model", "Ollama_Model"),
    }
    vars_to_check = env_vars_map.get(p, (f"{p.upper()}_MODEL",))

    for var in vars_to_check:
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    user_cfg = load_user_config()
    cfg_val = (
        user_cfg.get(f"{p}_model")
        or (user_cfg.get("model") if user_cfg.get("provider") == p or not user_cfg.get("provider") else None)
        or (user_cfg.get("groq_model") if p == "groq" else None)
    )
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return DEFAULT_MODELS.get(p, DEFAULT_GROQ_MODEL)


def get_ollama_host(override_host: Optional[str] = None) -> str:
    if override_host and override_host.strip():
        return override_host.strip()

    for var in ("OLLAMA_HOST", "ollama_host"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    user_cfg = load_user_config()
    cfg_val = user_cfg.get("ollama_host")
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return DEFAULT_OLLAMA_HOST


def mask_api_key(key: Optional[str]) -> str:
    clean = normalize_api_key(key)
    if not clean:
        return "Not configured"
    if len(clean) <= 8:
        return "*" * len(clean)
    return f"{clean[:4]}{'*' * 12}{clean[-4:]}"


def get_config_summary(provider: Optional[str] = None) -> Dict[str, Any]:
    p = get_provider(provider)
    model = get_model(provider=p)
    api_key = get_api_key(provider=p)
    ollama_host = get_ollama_host()
    config_path = str(get_config_path())
    user_cfg = load_user_config()

    key_source = "not set"
    if p != "ollama":
        env_vars = {
            "groq": ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"),
            "gemini": ("GEMINI_API_KEY", "gemini_api_key", "Gemini_Api_Key"),
            "openai": ("OPENAI_API_KEY", "openai_api_key", "Openai_Api_Key"),
        }.get(p, (f"{p.upper()}_API_KEY",))
        for var in env_vars:
            if os.getenv(var):
                key_source = f"environment ({var})"
                break
        if key_source == "not set" and (user_cfg.get(f"{p}_api_key") or (p == "groq" and user_cfg.get("groq_api_key"))):
            key_source = "user configuration"

    model_source = "default"
    for var in ("COMIT_MODEL", "comit_model"):
        if os.getenv(var):
            model_source = f"environment ({var})"
            break
    if model_source == "default":
        provider_model_vars = {
            "groq": ("GROQ_MODEL", "groq_model"),
            "gemini": ("GEMINI_MODEL", "gemini_model"),
            "openai": ("OPENAI_MODEL", "openai_model"),
            "ollama": ("OLLAMA_MODEL", "ollama_model"),
        }.get(p, ())
        for var in provider_model_vars:
            if os.getenv(var):
                model_source = f"environment ({var})"
                break
    if model_source == "default" and (user_cfg.get(f"{p}_model") or user_cfg.get("model") or (p == "groq" and user_cfg.get("groq_model"))):
        model_source = "user configuration"

    provider_source = "default"
    for var in ("COMIT_PROVIDER", "comit_provider"):
        if os.getenv(var):
            provider_source = f"environment ({var})"
            break
    if provider_source == "default" and user_cfg.get("provider"):
        provider_source = "user configuration"

    return {
        "provider": p,
        "provider_source": provider_source,
        "model": model,
        "model_source": model_source,
        "api_key_masked": mask_api_key(api_key) if p != "ollama" else "N/A (local)",
        "api_key_source": key_source if p != "ollama" else "N/A",
        "api_key_set": bool(api_key) if p != "ollama" else True,
        "ollama_host": ollama_host,
        "config_file": config_path,
        "config_exists": get_config_path().is_file(),
    }
