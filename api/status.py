"""Service status helpers."""
from __future__ import annotations

from api.docker_ops import compose_cmd, parse_ps, run, service_health
from shared.config import Config, ServiceConfig


def get_service_status(config: Config, service: ServiceConfig) -> dict:
    result = run(compose_cmd(config, service, "ps", "--format", "json", service.name), timeout=60)
    containers = parse_ps(result.stdout) if result.returncode == 0 else []
    return {
        "service": service.name,
        "health": service_health(config, service),
        "containers": [
            {
                "name": container.get("Name", ""),
                "state": container.get("State", ""),
                "health": container.get("Health", ""),
                "exit_code": container.get("ExitCode", 0),
            }
            for container in containers
        ],
    }
