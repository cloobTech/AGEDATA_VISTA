from services.data_processing.helper.upload_file import process_small_file
from services.data_processing.helper.upload_picture import process_image_file


file_processors = {
    "tabular": process_small_file,
    "image": process_image_file,
}


async def select_upload_processor(file, user_id, session, file_type):
    """Select approriate upload type"""

    if file_type not in file_processors:
        raise ValueError(
            f"Invalid file processor type, must be one of: {list(file_processors.keys())}")

    processor_func = file_processors[file_type]
    response = await processor_func(file, user_id, session)
    return response
