"""FastAPI application."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import docker_ops, log_ops, status
from shared.config import get_config

app = FastAPI(title="homeops", version="0.1.0")

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


def _service(name: str):
    config = get_config()
    service = config.services.get(name)
    if service is None:
        raise HTTPException(status_code=404, detail=f"unknown service: {name}")
    return config, service


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/api/services")
def list_services():
    config = get_config()
    return [
        {"name": service.name, "url": service.url, "critical": service.critical, "icon": service.icon}
        for service in config.services.values()
    ]


@app.get("/api/services/{name}/status")
def service_status(name: str):
    config, service = _service(name)
    return status.get_service_status(config, service)


@app.get("/api/services/{name}/logs")
def service_logs(name: str, tail: int = 200):
    config, service = _service(name)
    return log_ops.get_service_logs(config, service, tail=tail)


@app.post("/api/services/{name}/update")
def service_update(name: str):
    config, service = _service(name)
    result = docker_ops.update_service(config, service)
    return result.__dict__


@app.post("/api/services/{name}/start")
def service_start(name: str):
    config, service = _service(name)
    ok, detail = docker_ops.up(config, service)
    if not ok:
        raise HTTPException(status_code=500, detail=detail)
    return {"service": name, "result": detail}


@app.post("/api/services/{name}/stop")
def service_stop(name: str):
    config, service = _service(name)
    ok, detail = docker_ops.stop(config, service)
    if not ok:
        raise HTTPException(status_code=500, detail=detail)
    return {"service": name, "result": detail}


@app.post("/api/services/{name}/restart")
def service_restart(name: str):
    config, service = _service(name)
    ok, detail = docker_ops.restart(config, service)
    if not ok:
        raise HTTPException(status_code=500, detail=detail)
    return {"service": name, "result": detail}


if WEB_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/")
    def index():
        return FileResponse(WEB_DIR / "index.html")
