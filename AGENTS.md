# homeops

Repo del control plane del home-lab: un'unica app (backend API Docker + frontend dashboard + bot Telegram) che unisce i vecchi repo `dashboard` e `downscaler`.

## Stato

Baseline di documentazione. Il codice non e' ancora presente: questo repo parte da qui.

## Regole

- Branch + PR su `main`, mai push diretto.
- Le mappe (questo file e `docs/REFERENCE.md`) si aggiornano NELLA STESSA PR che le invalida.
- Limiti: 500 righe/file, 50 righe/funzione, niente fallback silenziosi.
- Compose: valori letterali, niente variabili template, niente `env_file`.
- Health poll: 30s, timeout massimo 10 poll (5 min) configurabile.

## Indice richiesta -> file

| Cosa devi fare | Dove guardare |
|---|---|
| Capire il progetto | questo file |
| Mappa richiesta -> file -> entry point | `docs/REFERENCE.md` |

## Documenti

| Doc | Stato | A cosa serve |
|---|---|---|
| `AGENTS.md` | ACTIVE | indice radice, regole |
| `docs/REFERENCE.md` | ACTIVE | mappa richiesta -> file |
