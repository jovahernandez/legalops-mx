#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
python -c "
import time, psycopg2, os
url = os.environ.get('DATABASE_URL', 'postgresql://legalops:legalops@db:5432/legalops')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
for i in range(30):
    try:
        conn = psycopg2.connect(url)
        conn.close()
        print('Connected!')
        break
    except Exception as e:
        print(f'Attempt {i+1}/30: {e}')
        time.sleep(1)
else:
    raise Exception('Could not connect to PostgreSQL after 30 attempts')
"

# --- Migrations (with advisory lock to avoid race conditions) ---
RUN_MIGRATIONS="${RUN_MIGRATIONS:-true}"
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Acquiring advisory lock and running migrations..."
  python -c "
import psycopg2, os, subprocess, sys
url = os.environ.get('DATABASE_URL', 'postgresql://legalops:legalops@db:5432/legalops')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)
conn = psycopg2.connect(url)
conn.autocommit = True
cur = conn.cursor()
# Advisory lock ID 1 = migrations lock
cur.execute('SELECT pg_try_advisory_lock(1)')
got_lock = cur.fetchone()[0]
if got_lock:
    print('Lock acquired – running alembic upgrade head')
    result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=False)
    cur.execute('SELECT pg_advisory_unlock(1)')
    if result.returncode != 0:
        sys.exit(result.returncode)
    print('Migrations complete, lock released.')
else:
    print('Another instance is running migrations – skipping.')
cur.close()
conn.close()
"
else
  echo "RUN_MIGRATIONS=false – skipping migrations."
fi

# --- Seed demo data (only when explicitly enabled) ---
SEED_DEMO="${SEED_DEMO:-false}"
if [ "$SEED_DEMO" = "true" ]; then
  echo "SEED_DEMO=true – seeding demo data..."
  python -m app.seed
else
  echo "SEED_DEMO=false – skipping seed."
fi

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
