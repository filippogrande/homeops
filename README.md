# homeops

Control plane per il home-lab: un'unica app che unisce il pannello di
controllo (`dashboard`) e il paracadute (`downscaler`).

## Componenti

- `api/` - backend FastAPI: comandi Docker Compose, stato, log, update con polling health
- `web/` - dashboard statica servita dall'API
- `telegram/` - bot sottile: inoltra i comandi all'API
- `shared/` - configurazione e logging JSON
- `docker/` - Dockerfile, compose e script di build

## Avvio locale

```
pip install -r requirements-dev.txt
pytest -q
uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## Docker

```
./docker/build.sh
docker compose -f docker/compose.yaml up -d
```

## Configurazione

Tutto in `config.yaml`: `compose_root`, soglie di update, Telegram e lista servizi.

## API

- `GET /api/services`
- `GET /api/services/{name}/status`
- `GET /api/services/{name}/logs?tail=200`
- `POST /api/services/{name}/update`
- `POST /api/services/{name}/start|stop|restart`

## Telegram

`/services`, `/update <servizio>`, `/start|/stop|/restart <servizio>`.
Solo i `chat_ids` in `config.yaml` possono comandare.
