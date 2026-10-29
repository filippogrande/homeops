# REFERENCE - homeops

Mappa richiesta -> file -> entry point. Le voci `pianificato` non esistono ancora: si compilano quando il file viene creato.

## Backend API (`api/`) - pianificato

| Richiesta | File | Entry point |
|---|---|---|
| Aggiornare un servizio (pull -> up -> polling health) | `api/docker_ops.py` | `update_service()` |
| Stato di un servizio | `api/status.py` | `get_service_status()` |
| Log di un servizio | `api/log_ops.py` | `get_service_logs()` |

## Configurazione (`shared/`) - pianificato

| Richiesta | File | Entry point |
|---|---|---|
| Caricare servizi e soglie | `shared/config.py` | `load_config()` |
| Whitelist chat Telegram | `shared/config.py` | `get_telegram_whitelist()` |

## Bot Telegram (`telegram/`) - pianificato

| Richiesta | File | Entry point |
|---|---|---|
| Comando /update <servizio> | `telegram/bot.py` | `handle_update()` |

## Frontend (`web/`) - pianificato

| Richiesta | File | Entry point |
|---|---|---|
| Dashboard | `web/app.py` | `create_app()` |

## Infra (`docker/`) - pianificato

| Richiesta | File | Entry point |
|---|---|---|
| Stack completo | `docker/compose.yaml` | - |
