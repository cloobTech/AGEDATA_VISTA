from celery_app import celery_app
from services.data_processing.helper.upload_file import process_small_file
from services.data_processing.helper.upload_picture import process_image_file

file_processors = {
    "tabular": process_small_file,
    "image": process_image_file,
}


async def select_upload_processor(file, form):
    """Select and trigger the appropriate file processor"""
    if form.file_type not in file_processors:
        raise ValueError(
            f"Invalid file processor type, must be one of: {list(file_processors.keys())}"
        )

    processor_func = file_processors[form.file_type]

    # Serialize form
    form_dict = form.dict()

    # Read file content if uploaded
    file_bytes = await file.read() if file else None
    file_name = file.filename if file else form.file_name or "uploaded_file"
    form_dict["file_name"] = file_name

    # Enqueue Celery task (non-blocking)
    task = processor_func.delay(form_dict, file_bytes)

    return {"task_id": task.id, "status": "queued"}
