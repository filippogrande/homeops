"""Configuration loading for homeops."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = os.environ.get("HOMEOPS_CONFIG", "/app/config.yaml")


@dataclass(frozen=True)
class UpdateSettings:
    poll_interval_sec: int = 30
    timeout_sec: int = 300


@dataclass(frozen=True)
class TelegramSettings:
    enabled: bool = False
    bot_token: str = ""
    chat_ids: tuple[int, ...] = ()
    api_base: str = "http://127.0.0.1:8000"


@dataclass(frozen=True)
class ServiceConfig:
    name: str
    compose_file: str
    url: str = ""
    critical: bool = False
    icon: str = ""


@dataclass(frozen=True)
class Config:
    compose_root: Path
    update: UpdateSettings
    telegram: TelegramSettings
    services: dict[str, ServiceConfig] = field(default_factory=dict)


def _service_from_dict(raw: dict[str, Any]) -> ServiceConfig:
    name = str(raw["name"]).strip()
    if not name:
        raise ValueError("service name cannot be empty")
    return ServiceConfig(
        name=name,
        compose_file=str(raw.get("compose_file", f"{name}/compose.yaml")),
        url=str(raw.get("url", "")),
        critical=bool(raw.get("critical", False)),
        icon=str(raw.get("icon", "")),
    )


def load_config(path: str | None = None) -> Config:
    config_path = Path(path or DEFAULT_CONFIG_PATH)
    if not config_path.is_file():
        raise FileNotFoundError(f"config not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    compose_root = Path(str(raw.get("compose_root", "/stacks")))
    update_raw = raw.get("update") or {}
    telegram_raw = raw.get("telegram") or {}
    services: dict[str, ServiceConfig] = {}
    for item in raw.get("services") or []:
        service = _service_from_dict(item)
        services[service.name] = service
    return Config(
        compose_root=compose_root,
        update=UpdateSettings(
            poll_interval_sec=int(update_raw.get("poll_interval_sec", 30)),
            timeout_sec=int(update_raw.get("timeout_sec", 300)),
        ),
        telegram=TelegramSettings(
            enabled=bool(telegram_raw.get("enabled", False)),
            bot_token=str(telegram_raw.get("bot_token", "")),
            chat_ids=tuple(int(c) for c in telegram_raw.get("chat_ids") or []),
            api_base=str(telegram_raw.get("api_base", "http://127.0.0.1:8000")),
        ),
        services=services,
    )


_cache: Config | None = None


def get_config() -> Config:
    global _cache
    if _cache is None:
        _cache = load_config()
    return _cache


def service_paths(config: Config, service: ServiceConfig) -> Path:
    return config.compose_root / service.compose_file
