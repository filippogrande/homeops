# REFERENCE - homeops

Mappa richiesta -> file -> entry point. Tutto ACTIVE.

## Backend API

| Richiesta | File | Entry point |
|---|---|---|
| Aggiornare un servizio (pull -> up -> polling health) | `api/docker_ops.py` | `update_service()` |
| Stato di un servizio | `api/status.py` | `get_service_status()` |
| Log di un servizio | `api/log_ops.py` | `get_service_logs()` |
| Endpoint HTTP | `api/app.py` | le funzioni `@app.*` |

## Configurazione e logging

| Richiesta | File | Entry point |
|---|---|---|
| Caricare servizi e soglie | `shared/config.py` | `load_config()`, `get_config()` |
| Formattare i log in JSON | `shared/logging.py` | `get_logger()` |

## Bot Telegram

| Richiesta | File | Entry point |
|---|---|---|
| Comando /update <servizio> | `telegram/bot.py` | `handle_command()`, `main()` |

## Frontend

| Richiesta | File | Entry point |
|---|---|---|
| Dashboard | `web/index.html`, `web/app.js` | `render()` |

## Infra

| Richiesta | File | Entry point |
|---|---|---|
| Immagine | `docker/Dockerfile` | - |
| Stack | `docker/compose.yaml` | - |
| Build | `docker/build.sh` | - |
