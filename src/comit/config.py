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


def get_api_key(override_key: Optional[str] = None) -> Optional[str]:
    if override_key and override_key.strip():
        return override_key.strip()

    for var in ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    for k, v in os.environ.items():
        if k.strip().lower() in ("groq_api_key", "groq_key") and v and v.strip():
            return v.strip()

    user_cfg = load_user_config()
    cfg_val = user_cfg.get("groq_api_key")
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return None


def get_model(override_model: Optional[str] = None) -> str:
    if override_model and override_model.strip():
        return override_model.strip()

    for var in ("GROQ_MODEL", "groq_model", "Groq_Model"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    user_cfg = load_user_config()
    cfg_val = user_cfg.get("groq_model") or user_cfg.get("model")
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return DEFAULT_GROQ_MODEL


def get_provider(override_provider: Optional[str] = None) -> str:
    if override_provider and override_provider.strip():
        return override_provider.strip()

    for var in ("COMIT_PROVIDER", "comit_provider"):
        val = os.getenv(var)
        if val and val.strip():
            return val.strip()

    user_cfg = load_user_config()
    cfg_val = user_cfg.get("provider")
    if cfg_val and str(cfg_val).strip():
        return str(cfg_val).strip()

    return DEFAULT_PROVIDER


def mask_api_key(key: Optional[str]) -> str:
    if not key or not key.strip():
        return "Not configured"
    clean = key.strip()
    if len(clean) <= 8:
        return "*" * len(clean)
    return f"{clean[:4]}{'*' * 12}{clean[-4:]}"


def get_config_summary() -> Dict[str, Any]:
    api_key = get_api_key()
    model = get_model()
    provider = get_provider()
    config_path = str(get_config_path())
    
    key_source = "not set"
    for var in ("GROQ_API_KEY", "groq_api_key", "Groq_Api_Key", "GROQ_KEY"):
        if os.getenv(var):
            key_source = f"environment ({var})"
            break
    if key_source == "not set" and load_user_config().get("groq_api_key"):
        key_source = "user configuration"

    model_source = "default"
    for var in ("GROQ_MODEL", "groq_model", "Groq_Model"):
        if os.getenv(var):
            model_source = f"environment ({var})"
            break
    if model_source == "default" and (load_user_config().get("groq_model") or load_user_config().get("model")):
        model_source = "user configuration"

    return {
        "provider": provider,
        "model": model,
        "model_source": model_source,
        "api_key_masked": mask_api_key(api_key),
        "api_key_source": key_source,
        "api_key_set": bool(api_key),
        "config_file": config_path,
        "config_exists": get_config_path().is_file(),
    }
