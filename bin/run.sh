#!/usr/bin/env bash
# Canonical run command (venv + uvicorn). Safe + idempotent; systemd (app@) calls this.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -x .venv/bin/uvicorn ]; then python3 -m venv .venv; .venv/bin/pip install -r requirements.txt; fi
[ -f .env ] && { set -a; . ./.env; set +a; }
exec .venv/bin/uvicorn mekarpeles.asgi:app --host 127.0.0.1 --port "${PORT:-8090}"
