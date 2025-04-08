from urllib.parse import urlparse
import os

def extract_public_id(full_url):
    parsed = urlparse(full_url)
    path_parts = parsed.path.split("/")  # breaks it into ['/', 'raw', 'upload', 'v123', 'folder', 'filename']
    
    try:
        upload_index = path_parts.index("upload")
        public_id_with_ext = "/".join(path_parts[upload_index + 2:])  # skip 'upload' and version
        public_id, _ = os.path.splitext(public_id_with_ext)  # remove extension
        return public_id
    except ValueError:
        return None
