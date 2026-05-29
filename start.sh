#!/bin/bash
set -e

SERVICE_TYPE="${SERVICE_TYPE:-api}"

if [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery worker..."
    exec celery -A celery_app.celery_app worker --loglevel=info --concurrency="${CELERY_CONCURRENCY:-4}"

elif [ "$SERVICE_TYPE" = "beat" ]; then
    echo "Starting Celery beat..."
    exec celery -A celery_app.celery_app beat --loglevel=info

else
    echo "Running database migrations..."
    alembic upgrade head
    echo "Starting API server..."
    exec gunicorn api.v1.main:app \
        -k uvicorn.workers.UvicornWorker \
        --bind "0.0.0.0:${PORT:-8000}" \
        --workers "${WEB_CONCURRENCY:-2}" \
        --timeout 120 \
        --access-logfile -
fi
