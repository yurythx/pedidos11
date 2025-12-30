#!/bin/sh
set -e
python manage.py migrate --noinput
python manage.py create_default_superuser || true
if [ "${RUN_SEED_INIT:-False}" = "True" ] || [ "${RUN_SEED_INIT:-false}" = "true" ]; then
  python manage.py seed_init || true
fi
python manage.py collectstatic --noinput
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-3}
