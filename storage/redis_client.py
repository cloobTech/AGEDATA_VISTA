import redis.asyncio as redis
from settings.pydantic_config import settings
from typing import Optional, Dict, Any
import json

# redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
redis_client = redis.from_url(
    "redis://localhost:6379/1", decode_responses=True
)


# storage/redis_client.py
async def set_task_progress(task_id: str, progress: int, status: str, message: str = ""):
    """Set task progress in Redis with proper type handling"""
    try:
        # Validate inputs
        if not task_id or not isinstance(task_id, str):
            raise ValueError(f"Invalid task_id: {task_id}")

        # Ensure all values are strings/ints, not None
        data = {
            "progress": int(progress),
            "status": str(status) if status else "UNKNOWN",
            "message": str(message) if message is not None else ""
        }

        print(f"📊 Setting task progress: {task_id} - {data}")  # Debug log

        await redis_client.hset(
            f"task:{task_id}",
            mapping=data
        )
        # Set expiration (e.g., 1 hour)
        await redis_client.expire(f"task:{task_id}", 3600)
    except Exception as e:
        print(f"❌ Error setting task progress for {task_id}: {e}")
        raise


async def set_temp_data(task_id: str, data: dict, expire: int = 3600):
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

        await redis_client.hset(
            f"temp:{task_id}",
            mapping=safe_data
        )
        await redis_client.expire(f"temp:{task_id}", expire)
    except Exception as e:
        print(f"❌ Error setting temp data for {task_id}: {e}")
        raise


async def get_temp_data(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve temporary data from Redis."""
    result = await redis_client.hgetall(f"temp:{task_id}")  # type: ignore
    return result if result else None


async def get_task_progress(task_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve task progress and status from Redis."""
    result = await redis_client.hgetall(f"task:{task_id}")  # type: ignore
    return result if result else None


async def delete_task_progress(task_id: str):
    """Delete task progress from Redis."""
    await redis_client.delete(f"task:{task_id}")


async def set_task_complete(task_id: str, result: str = "SUCCESS"):
    """Mark task as completed."""
    await set_task_progress(task_id, progress=100, status=result)


async def set_task_failed(task_id: str, error_message: str = "FAILED"):
    """Mark task as failed."""
    await set_task_progress(task_id, progress=100, status=f"FAILED: {error_message}")
