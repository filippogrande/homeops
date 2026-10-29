#!/bin/sh
set -e

python -m telegram.bot &
exec uvicorn api.app:app --host 0.0.0.0 --port 8000
