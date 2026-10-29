from pathlib import Path

import api.docker_ops as ops
from shared.config import Config, ServiceConfig, TelegramSettings, UpdateSettings

SERVICE = ServiceConfig(name="nextcloud", compose_file="nc/compose.yaml")


def make_config() -> Config:
    return Config(
        compose_root=Path("/stacks"),
        update=UpdateSettings(poll_interval_sec=0, timeout_sec=1),
        telegram=TelegramSettings(),
        services={},
    )


def test_update_up_to_date(monkeypatch):
    monkeypatch.setattr(ops, "pull", lambda config, service: (True, "up_to_date"))
    monkeypatch.setattr(ops, "service_health", lambda config, service: "healthy")
    result = ops.update_service(make_config(), SERVICE)
    assert result.status == "up_to_date"


def test_update_updated(monkeypatch):
    monkeypatch.setattr(ops, "pull", lambda config, service: (True, "pulled"))
    monkeypatch.setattr(ops, "up", lambda config, service: (True, "started"))
    monkeypatch.setattr(ops, "wait_healthy", lambda config, service: (True, "healthy", 3))
    result = ops.update_service(make_config(), SERVICE)
    assert result.status == "updated"
    assert result.polls == 3


def test_update_pull_failure(monkeypatch):
    monkeypatch.setattr(ops, "pull", lambda config, service: (False, "boom"))
    result = ops.update_service(make_config(), SERVICE)
    assert result.status == "failed"
    assert "pull failed" in result.detail


def test_update_health_timeout(monkeypatch):
    monkeypatch.setattr(ops, "pull", lambda config, service: (True, "pulled"))
    monkeypatch.setattr(ops, "up", lambda config, service: (True, "started"))
    monkeypatch.setattr(ops, "wait_healthy", lambda config, service: (False, "unhealthy", 2))
    result = ops.update_service(make_config(), SERVICE)
    assert result.status == "failed"
    assert "timeout" in result.detail


def test_update_busy(monkeypatch):
    lock = ops._lock_for("nextcloud")
    lock.acquire()
    try:
        result = ops.update_service(make_config(), SERVICE)
    finally:
        lock.release()
    assert result.status == "busy"


def test_run_handles_missing_binary(monkeypatch):
    import subprocess

    def boom(*args, **kwargs):
        raise FileNotFoundError("docker")

    monkeypatch.setattr(subprocess, "run", boom)
    result = ops.run(["docker", "version"], timeout=1)
    assert result.returncode == 127


def test_run_handles_timeout(monkeypatch):
    import subprocess

    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="docker", timeout=1)

    monkeypatch.setattr(subprocess, "run", boom)
    result = ops.run(["docker", "version"], timeout=1)
    assert result.returncode == 124
