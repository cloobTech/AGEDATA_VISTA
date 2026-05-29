# services/sse/server_sent_events.py
import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from storage.redis_client import get_task_progress, get_temp_data


class SSEService:
    def __init__(self):
        self.max_retries = 120   # 2-minute hard cap (was 300 / 5 min)
        self.poll_interval = 1
        self.no_data_timeout = 20  # seconds before declaring worker unavailable

    async def stream_task_progress(self, task_id: str, request: Request):
        print(f"🎯 SSE connection started for task: {task_id}")

        async def event_generator():
            last_progress = 0
            last_status = ""
            retries = 0

            while retries < self.max_retries:
                if await request.is_disconnected():
                    print(f"🔌 SSE connection disconnected for task: {task_id}")
                    break

                try:
                    progress_data = await get_task_progress(task_id)
                    temp_data = await get_temp_data(task_id)

                    if progress_data:
                        progress = progress_data.get("progress", 0)
                        status = progress_data.get("status", "UNKNOWN")
                        message = progress_data.get("message", "")
                        file_type = temp_data.get(
                            "file_type", "unknown") if temp_data else "unknown"

                        print(f"📊 Redis data - Progress: {progress}, Status: {status}, Message: {message}")

                        should_send_event = (
                            progress != last_progress or
                            status != last_status or
                            status in ["COMPLETED", "FAILED", "STARTED", "SAVING_TO_DATABASE",
                                       "UPLOADING_TO_EXTERNAL_STORAGE", "CLEANING_DATA",
                                       "DOWNLOADING_FILE", "RUNNING"] or
                            retries == 0
                        )

                        if should_send_event:
                            event_data = {
                                "task_id": task_id,
                                "progress": progress,
                                "status": status,
                                "message": message,
                                "file_type": file_type,
                                "data": temp_data or {}
                            }
                            print(f"📤 Sending SSE event - Task: {task_id}, Progress: {progress}%, Status: {status}")
                            yield f"data: {json.dumps(event_data)}\n\n"
                            last_progress = progress
                            last_status = status

                        if status in ["COMPLETED", "FAILED"]:
                            print(f"✅ SSE connection completed for task: {task_id}")
                            break

                    else:
                        # No Redis data yet — task is queued but not started
                        if retries == 0:
                            # Immediate heartbeat so the UI shows something straight away
                            yield f"data: {json.dumps({'task_id': task_id, 'progress': 0, 'status': 'QUEUED', 'message': 'Task queued, waiting for worker…'})}\n\n"
                            print(f"📤 Sent QUEUED heartbeat for task: {task_id}")
                        elif retries >= self.no_data_timeout:
                            # Worker not picking up after ~20 s — surface the error instead of hanging
                            print(f"⚠️  No worker activity after {self.no_data_timeout}s for task: {task_id}")
                            yield f"data: {json.dumps({'task_id': task_id, 'progress': 0, 'status': 'WORKER_UNAVAILABLE', 'message': 'Celery worker is not running. Start it with: cd backend && python run_celery_autoreload.py'})}\n\n"
                            break

                    await asyncio.sleep(self.poll_interval)
                    retries += 1

                except Exception as e:
                    print(f"❌ SSE Error for task {task_id}: {str(e)}")
                    error_data = {
                        "task_id": task_id,
                        "progress": 100,
                        "status": "ERROR",
                        "message": f"Error monitoring task: {str(e)}",
                        "file_type": "unknown",
                        "data": {}
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    break

            if retries >= self.max_retries:
                print(f"⏰ SSE timeout for task: {task_id}")
                timeout_data = {
                    "task_id": task_id,
                    "progress": 100,
                    "status": "TIMEOUT",
                    "message": "Task monitoring timeout",
                    "file_type": "unknown",
                    "data": {}
                }
                yield f"data: {json.dumps(timeout_data)}\n\n"

        response = StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )

        print(f"🚀 Returning SSE response for task: {task_id}")
        return response


sse_service = SSEService()
