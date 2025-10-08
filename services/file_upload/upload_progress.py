from storage.redis_client import get_task_progress, get_temp_data


class TaskProgressService:
    async def get_task_status(self, task_id: str):
        """Get current task status"""
        progress_data = await get_task_progress(task_id)
        temp_data = await get_temp_data(task_id)
        
        if not progress_data:
            return {
                "task_id": task_id,
                "status": "NOT_FOUND",
                "progress": 0,
                "message": "Task not found",
                "data": {}
            }
        
        return {
            "task_id": task_id,
            "progress": progress_data.get("progress", 0),
            "status": progress_data.get("status", "UNKNOWN"),
            "message": progress_data.get("message", ""),
            "data": temp_data or {}
        }


task_progress_service = TaskProgressService()