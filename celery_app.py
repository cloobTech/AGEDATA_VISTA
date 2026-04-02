import os
from celery import Celery
from settings.pydantic_config import settings
from celery.schedules import crontab

# Prefer CELERY_BROKER_URL (supports password: redis://:pass@host:port/db).
# Fall back to REDIS_URL with database index appended.
# NEVER hard-code the password — load it from environment only.
_redis_base = settings.REDIS_URL.rstrip('/')
_celery_broker = os.environ.get("CELERY_BROKER_URL") or f"{_redis_base}/0"
_celery_backend = os.environ.get("CELERY_RESULT_BACKEND") or f"{_redis_base}/1"

broker = _celery_broker
backend = _celery_backend
celery_app = Celery('worker', broker=broker, backend=backend)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Prevent deserialization of untrusted data — json only
    broker_transport_options={'visibility_timeout': 3600},
    include=[
        'services.data_processing.helper.upload_file',
        'services.data_processing.helper.upload_picture',
        'services.data_processing.large_data.big_data_task',
        'tasks.expire_trial_sub',
    ],
)

celery_app.conf.beat_schedule = {
    "expire-trials-every-hour": {
        "task": "expire_subscriptions",
        "schedule": crontab(minute=0, hour="*"),

    }
}


# celery_app.autodiscover_tasks(["services.data_processing.helper"])
