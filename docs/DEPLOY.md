# Deploy

## Build

```
./docker/build.sh
```

## Avvio

```
docker compose -f docker/compose.yaml up -d
```

`docker/compose.yaml` monta:

- `/var/run/docker.sock` - per eseguire i comandi docker
- `/mnt/applicazioni/yml/docker` -> `/stacks` - dove vivono i compose
- `./config.yaml` -> `/app/config.yaml` (read-only)

## Verifica

```
curl -s localhost:8090/healthz
curl -s localhost:8090/api/services
```

## Note

- Dopo aver modificato `config.yaml` serve un restart del container.
- Dopo aver modificato il compose serve `docker compose down && docker compose up -d`:
  `up -d` da solo puo' riusare il container vecchio.
- Telegram si attiva mettendo `telegram.enabled: true` e il token in `config.yaml`.
