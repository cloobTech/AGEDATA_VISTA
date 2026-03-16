from celery import Celery
from settings.pydantic_config import settings
from celery.schedules import crontab


# broker = "redis://localhost:6379/0"
# backend = "redis://localhost:6379/1"
_redis_base = settings.REDIS_URL.rstrip('/')
broker = f"{_redis_base}/0"
backend = f"{_redis_base}/1"
celery_app = Celery('worker', broker=broker, backend=backend)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    include=['services.data_processing.helper.upload_file',
             'services.data_processing.helper.upload_picture',
             'services.data_processing.large_data.big_data_task',
             'tasks.expire_trial_sub'
             ]
)

celery_app.conf.beat_schedule = {
    "expire-trials-every-hour": {
        "task": "expire_subscriptions",
        "schedule": crontab(minute=0, hour="*"),

    }
}


# celery_app.autodiscover_tasks(["services.data_processing.helper"])
