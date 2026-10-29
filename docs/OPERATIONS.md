# Operazioni

## Aggiornare un servizio

Da Telegram: `/update nextcloud`.
Da dashboard: pulsante Aggiorna.
Da API: `POST /api/services/nextcloud/update`.

Esiti: `updated`, `up_to_date`, `failed`, `busy` (update gia' in corso).

## Vedere lo stato

`GET /api/services/{name}/status` oppure il badge nella dashboard.

## Leggere i log

`GET /api/services/{name}/logs?tail=200` oppure pulsante Log.

## Aggiungere un servizio

1. Aggiungere il compose sotto `compose_root` (default `/stacks`).
2. Aggiungere la voce in `config.yaml` sotto `services`.
3. Riavviare il container homeops (la config si legge all'avvio).
