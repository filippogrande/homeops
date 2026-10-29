"""Docker Compose operations: update, status, logs."""
from __future__ import annotations

import json
import subprocess
import threading
import time
from dataclasses import dataclass

from shared.config import Config, ServiceConfig, service_paths
from shared.logging import get_logger

logger = get_logger(__name__)

_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(name: str) -> threading.Lock:
    with _locks_guard:
        if name not in _locks:
            _locks[name] = threading.Lock()
        return _locks[name]


@dataclass
class UpdateResult:
    service: str
    status: str
    detail: str = ""
    polls: int = 0
    elapsed_sec: float = 0.0


def compose_cmd(config: Config, service: ServiceConfig, *args: str) -> list[str]:
    return ["docker", "compose", "-f", str(service_paths(config, service)), *args]


def run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    logger.info("exec %s", " ".join(cmd))
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 124, "", f"timeout after {timeout}s")
    except FileNotFoundError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", f"command not found: {exc}")


def parse_ps(stdout: str) -> list[dict]:
    text = (stdout or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [data]
    containers: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            containers.append(item)
    return containers


def health_of(containers: list[dict]) -> str:
    if not containers:
        return "missing"
    states = [str(c.get("State", "")).lower() for c in containers]
    healths = [str(c.get("Health", "")).lower() for c in containers]
    if any(state != "running" for state in states):
        return "unhealthy"
    if any(health == "unhealthy" for health in healths):
        return "unhealthy"
    if any(health == "starting" for health in healths):
        return "starting"
    return "healthy"


def service_health(config: Config, service: ServiceConfig) -> str:
    result = run(compose_cmd(config, service, "ps", "--format", "json", service.name), timeout=60)
    if result.returncode != 0:
        return "unknown"
    return health_of(parse_ps(result.stdout))


def pull(config: Config, service: ServiceConfig) -> tuple[bool, str]:
    result = run(compose_cmd(config, service, "pull", service.name), timeout=900)
    if result.returncode != 0:
        return False, result.stderr.strip()
    output = (result.stdout or "").lower()
    if "up-to-date" in output or "up to date" in output or "nothing to pull" in output:
        return True, "up_to_date"
    return True, "pulled"


def up(config: Config, service: ServiceConfig) -> tuple[bool, str]:
    result = run(compose_cmd(config, service, "up", "-d", service.name), timeout=600)
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, "started"


def stop(config: Config, service: ServiceConfig) -> tuple[bool, str]:
    result = run(compose_cmd(config, service, "stop", service.name), timeout=120)
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, "stopped"


def restart(config: Config, service: ServiceConfig) -> tuple[bool, str]:
    result = run(compose_cmd(config, service, "restart", service.name), timeout=300)
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, "restarted"


def wait_healthy(config: Config, service: ServiceConfig) -> tuple[bool, str, int]:
    interval = config.update.poll_interval_sec
    deadline = time.monotonic() + config.update.timeout_sec
    polls = 0
    last = "unknown"
    consecutive_unhealthy = 0
    while time.monotonic() < deadline:
        polls += 1
        last = service_health(config, service)
        if last == "healthy":
            return True, last, polls
        if last == "unhealthy":
            consecutive_unhealthy += 1
            if consecutive_unhealthy >= 2:
                return False, last, polls
        else:
            consecutive_unhealthy = 0
        time.sleep(interval)
    return False, last, polls


def update_service(config: Config, service: ServiceConfig) -> UpdateResult:
    started = time.monotonic()
    lock = _lock_for(service.name)
    if not lock.acquire(blocking=False):
        return UpdateResult(service.name, "busy", "update already running")
    try:
        ok, detail = pull(config, service)
        if not ok:
            return UpdateResult(service.name, "failed", f"pull failed: {detail}", 0, time.monotonic() - started)
        if detail == "up_to_date" and service_health(config, service) == "healthy":
            return UpdateResult(service.name, "up_to_date", "already healthy", 0, time.monotonic() - started)
        ok, detail = up(config, service)
        if not ok:
            return UpdateResult(service.name, "failed", f"up failed: {detail}", 0, time.monotonic() - started)
        healthy, state, polls = wait_healthy(config, service)
        elapsed = time.monotonic() - started
        if healthy:
            return UpdateResult(service.name, "updated", state, polls, elapsed)
        return UpdateResult(service.name, "failed", f"health timeout, last state: {state}", polls, elapsed)
    finally:
        lock.release()
