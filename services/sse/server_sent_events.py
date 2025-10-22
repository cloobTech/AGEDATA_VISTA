# services/sse/server_sent_events.py
import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from storage.redis_client import get_task_progress, get_temp_data


class SSEService:
    def __init__(self):
        self.max_retries = 300
        self.poll_interval = 1

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

                        # Debug logging
                        print(
                            f"📊 Redis data - Progress: {progress}, Status: {status}, Message: {message}")

                        # Send event if:
                        # 1. Progress changed OR
                        # 2. Status changed OR
                        # 3. Status is important (COMPLETED, FAILED, etc.) OR
                        # 4. It's the first update
                        should_send_event = (
                            progress != last_progress or
                            status != last_status or
                            status in ["COMPLETED", "FAILED", "STARTED", "SAVING_TO_DATABASE", "UPLOADING_TO_EXTERNAL_STORAGE", "CLEANING_DATA", "DOWNLOADING_FILE", "RUNNING"] or
                            retries == 0  # Always send first update
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

                            print(
                                f"📤 Sending SSE event - Task: {task_id}, Progress: {progress}%, Status: {status}, Message: {message}")

                            yield f"data: {json.dumps(event_data)}\n\n"

                            # Update last values
                            last_progress = progress
                            last_status = status

                        # Stop if task is completed or failed
                        if status in ["COMPLETED", "FAILED"]:
                            print(
                                f"✅ SSE connection completed for task: {task_id}")
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
