#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/apps/api"
mkdir -p data/uploads
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi
export DATABASE_URL="${DATABASE_URL:-sqlite:///./data/acronyms.db}"
python -c "
from app.db import init_db, SessionLocal
from app.seed import seed_demo
init_db()
session = SessionLocal()
try:
    n = seed_demo(session)
    print(f'Seeded {n} new demo terms')
finally:
    session.close()
"
