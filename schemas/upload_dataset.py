from pydantic import BaseModel

class UploadForm(BaseModel):
    user_id: str
    file_type: str = "tabular"
    clean_file: bool = False
    source_type: str  # "upload" or "url"
    file_url: str | None = None

