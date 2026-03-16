import redis
from settings.pydantic_config import settings
import json



import urllib.parse as _urlparse
_redis_parsed = _urlparse.urlparse(settings.REDIS_URL)
# Synchronous Redis client for Celery tasks
redis_sync_client = redis.Redis(
    host=_redis_parsed.hostname or 'localhost',
    port=_redis_parsed.port or 6379,
    db=1,  # Use same DB as async client for consistency
    password=_redis_parsed.password,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
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

def set_temp_data_sync(task_id: str, data: dict, expire: int = 3600):
    """Set temporary data in Redis with proper type handling"""
    try:
        # Validate task_id
        if not task_id or not isinstance(task_id, str):
            raise ValueError(f"Invalid task_id: {task_id}")

        # Convert all values to strings and handle None values
        safe_data = {}
        for key, value in data.items():
            if value is None:
                safe_data[key] = ""
            elif isinstance(value, (dict, list)):
                safe_data[key] = json.dumps(value)
            else:
                safe_data[key] = str(value)

        print(f"💾 Setting temp data: {task_id} - {safe_data}")  # Debug log

        redis_sync_client.hset(
            f"temp:{task_id}",
            mapping=safe_data
        )
        redis_sync_client.expire(f"temp:{task_id}", expire)
    except Exception as e:
        print(f"❌ Error setting temp data for {task_id}: {e}")
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
