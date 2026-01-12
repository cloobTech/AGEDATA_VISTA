from urllib.parse import urlparse, unquote

def extract_cloudinary_public_id_and_type(url: str) -> tuple[str, str]:
    """
    Safely extracts (public_id, resource_type) from old or new Cloudinary URLs.
    Never raises for legacy URLs.
    """

    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < 3:
        return None, None

    # resource type is always first
    resource_type = path_parts[0]

    try:
        upload_index = path_parts.index("upload")
    except ValueError:
        return None, None

    # Everything AFTER 'upload' may include:
    # - transformations
    # - version (v123)
    # - public_id
    after_upload = path_parts[upload_index + 1 :]

    # Remove version segment if present
    if after_upload and after_upload[0].startswith("v"):
        after_upload = after_upload[1:]

    public_id = "/".join(after_upload)
    public_id = unquote(public_id)

    return public_id, resource_type
