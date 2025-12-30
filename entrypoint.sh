#!/bin/sh
set -e
echo "Aguardando Postgres em ${DB_HOST:-db}:${DB_PORT:-5432}..."
until python - <<'PYCODE'
import os
import sys
import time
try:
    import psycopg2
except Exception as e:
    sys.exit(0)
try:
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'pedidos11'),
        user=os.getenv('DB_USER', 'pedidos11'),
        password=os.getenv('DB_PASSWORD', ''),
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
PYCODE
do
  sleep 2
done
python manage.py migrate --noinput
python manage.py create_default_superuser || true
if [ "${RUN_SEED_INIT:-False}" = "True" ] || [ "${RUN_SEED_INIT:-false}" = "true" ]; then
  python manage.py seed_init || true
fi
python manage.py collectstatic --noinput
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3}
