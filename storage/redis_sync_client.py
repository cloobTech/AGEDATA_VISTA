import redis
from settings.pydantic_config import settings


# Synchronous Redis client for Celery tasks
redis_sync_client = redis.Redis(
    host='localhost',
    port=6379,
    db=3,  # Database number
    decode_responses=True
)



def set_task_progress_sync(task_id: str, progress: int, status: str, message: str = ""):
    """Synchronous version for Celery tasks"""
    try:
        data = {
            "progress": int(progress),
            "status": str(status) if status else "UNKNOWN",
            "message": str(message) if message is not None else ""
        }

        print(f"📊 Setting task progress (sync): {task_id} - {data}")

        redis_sync_client.hset(
            f"task:{task_id}",
            mapping=data
        )
        redis_sync_client.expire(f"task:{task_id}", 3600)
    except Exception as e:
        print(f"❌ Error setting task progress for {task_id}: {e}")
        raise


def set_task_complete_sync(task_id: str, result: str = "SUCCESS"):
    """Synchronous version for Celery tasks"""
    set_task_progress_sync(task_id, progress=100, status=result)


def set_task_failed_sync(task_id: str, error_message: str = "FAILED"):
    """Synchronous version for Celery tasks"""
    set_task_progress_sync(task_id, progress=100,
                           status=f"FAILED: {error_message}")


def get_task_progress_sync(task_id: str):
    """Synchronous version for getting task progress"""
    try:
        result = redis_sync_client.hgetall(f"task:{task_id}")
        return result if result else None
    except Exception as e:
        print(f"❌ Error getting task progress for {task_id}: {e}")
        return None
