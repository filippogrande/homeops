# Architettura

## Componenti

- API FastAPI (`api/app.py`) - espone HTTP e serve la dashboard.
- Docker ops (`api/docker_ops.py`) - pull, up, stop, restart, polling health.
- Config (`shared/config.py`) - legge `config.yaml`.
- Logging (`shared/logging.py`) - JSON su stdout.
- Bot (`telegram/bot.py`) - long polling Telegram, chiama l'API.
- Web (`web/`) - HTML/CSS/JS statico.

## Flusso update

1. Bot o dashboard chiama `POST /api/services/{name}/update`.
2. `update_service` acquisisce il lock del servizio (anti-flood).
3. `docker compose pull <svc>`.
4. Se l'immagine e' identica e il servizio e' gia' healthy -> `up_to_date`.
5. `docker compose up -d <svc>`.
6. Poll di `docker compose ps --format json` ogni `poll_interval_sec`.
7. Healthy -> `updated`. Due poll `unhealthy` consecutivi o timeout -> `failed`.

## Stato

`docker compose ps --format json` viene normalizzato:

- nessun container -> `missing`
- uno `State != running` o `Health = unhealthy` -> `unhealthy`
- `Health = starting` -> `starting`
- altrimenti `healthy`

## Sicurezza

- Il container monta `/var/run/docker.sock`: accesso root-equivalente. Tenere l'API su rete privata.
- Bot: whitelist `chat_ids`.
- Nessun comando arbitrario: solo azioni predefinite sull'elenco servizi.
