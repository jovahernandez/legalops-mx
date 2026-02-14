#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
python -c "
import time, psycopg2, os
url = os.environ.get('DATABASE_URL', 'postgresql://legalops:legalops@db:5432/legalops')
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

echo "Running migrations..."
alembic upgrade head

echo "Seeding data..."
python -m app.seed

echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
