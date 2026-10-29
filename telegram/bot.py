"""Telegram bot: thin wrapper over the homeops API."""
from __future__ import annotations

import time

import requests

from shared.config import get_config
from shared.logging import get_logger

logger = get_logger(__name__)

POLL_TIMEOUT = 50
HELP = (
    "Comandi: /services | /update <servizio> | /start <servizio> | "
    "/stop <servizio> | /restart <servizio>"
)


def api_get(base: str, path: str) -> requests.Response:
    return requests.get(f"{base}{path}", timeout=30)


def api_post(base: str, path: str) -> requests.Response:
    return requests.post(f"{base}{path}", timeout=900)


def send(token: str, chat_id: int, text: str) -> None:
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=30,
    )


def handle_command(base: str, text: str) -> str:
    parts = text.strip().split()
    command = parts[0].split("@")[0].lower() if parts else ""
    if command == "/services":
        names = [item["name"] for item in api_get(base, "/api/services").json()]
        return "Servizi:\n" + "\n".join(f"- {name}" for name in names)
    if command in {"/update", "/start", "/stop", "/restart"} and len(parts) >= 2:
        name = parts[1].lower()
        if command == "/update":
            body = api_post(base, f"/api/services/{name}/update").json()
            if body.get("status") in {"updated", "up_to_date"}:
                polls = body.get("polls", 0)
                elapsed = body.get("elapsed_sec", 0)
                return f"{name}: {body.get('status')} ({polls} poll, {elapsed:.0f}s)"
            return f"{name}: FALLITO - {body.get('detail', 'errore')}"
        response = api_post(base, f"/api/services/{name}{command}")
        if response.status_code >= 400:
            return f"{name}: errore {response.status_code}"
        return f"{name}: {response.json().get('result', 'ok')}"
    return HELP


def main() -> None:
    config = get_config()
    if not config.telegram.enabled or not config.telegram.bot_token:
        logger.info("telegram disabled, exiting")
        return
    token = config.telegram.bot_token
    base = config.telegram.api_base
    allowed = set(config.telegram.chat_ids)
    offset = 0
    logger.info("telegram bot started")
    while True:
        try:
            response = requests.get(
                f"https://api.telegram.org/bot{token}/getUpdates",
                params={"offset": offset, "timeout": POLL_TIMEOUT},
                timeout=60,
            )
            for update in response.json().get("result", []):
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                chat_id = (message.get("chat") or {}).get("id")
                text = message.get("text", "")
                if chat_id not in allowed or not text.startswith("/"):
                    continue
                try:
                    answer = handle_command(base, text)
                except Exception as exc:
                    logger.exception("command failed")
                    answer = f"Errore: {exc}"
                send(token, chat_id, answer)
        except Exception:
            logger.exception("poll failed")
            time.sleep(5)


if __name__ == "__main__":
    main()
