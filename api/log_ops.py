"""Log retrieval."""
from __future__ import annotations

from api.docker_ops import compose_cmd, run
from shared.config import Config, ServiceConfig


def get_service_logs(config: Config, service: ServiceConfig, tail: int = 200) -> dict:
    result = run(
        compose_cmd(config, service, "logs", "--no-color", "--tail", str(tail), service.name),
        timeout=60,
    )
    return {
        "service": service.name,
        "returncode": result.returncode,
        "logs": (result.stdout or "") + (result.stderr or ""),
    }
