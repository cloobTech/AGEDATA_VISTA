"""
safe_path.py — Path traversal prevention utility.

All file operations that resolve user-supplied or DB-stored URLs to local paths
MUST use safe_local_path() instead of a bare os.path.join(base, user_input).

CWE-22 (Path Traversal): an attacker could supply a file URL such as
  ../../etc/shadow
to escape the intended storage root.  safe_local_path() normalises the
candidate path and rejects anything that does not remain inside ALLOWED_BASE.

URL convention in this project:
  Database URLs are stored as ``/uploads/datasets/<filename>`` (root-relative).
  The backend stores files in ``<backend_root>/uploads/``.
  ALLOWED_BASE therefore points at the backend root, and the full URL path
  component is joined with it to reproduce the correct absolute path.
  Only resolved paths that start with ``<backend_root>/uploads/`` are accepted.
"""

import os

# The backend root is the parent of this file's parent (utils/ → backend/).
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ALLOWED_BASE is the backend root; we additionally restrict to the uploads
# sub-tree.  FILE_STORAGE_ROOT can override the backend root in .env.
ALLOWED_BASE = os.path.abspath(
    os.environ.get("FILE_STORAGE_ROOT", _BACKEND_ROOT)
)
# Only files under this sub-directory are permitted.
_ALLOWED_UPLOADS = os.path.join(ALLOWED_BASE, "uploads")


def safe_local_path(file_url: str) -> str:
    """Resolve *file_url* to an absolute path and reject traversal attempts.

    Args:
        file_url: A root-relative path stored in the database, e.g.
                  ``/uploads/datasets/abc123_data.csv``.

    Returns:
        The normalised absolute path, guaranteed to be inside
        ``<ALLOWED_BASE>/uploads/``.

    Raises:
        ValueError: If the resolved path would escape the uploads directory
                    (path traversal attempt).

    Examples::

        safe_local_path('/uploads/datasets/abc.csv')
        # → '<backend_root>/uploads/datasets/abc.csv'  ✅

        safe_local_path('../../etc/shadow')
        # → raises ValueError  ❌
    """
    # Strip leading slash so os.path.join treats the URL as relative to base
    stripped = file_url.lstrip("/")
    candidate = os.path.normpath(os.path.join(ALLOWED_BASE, stripped))
    # Resolved path must stay inside <backend_root>/uploads/
    allowed_prefix = _ALLOWED_UPLOADS + os.sep
    if not (candidate == _ALLOWED_UPLOADS or candidate.startswith(allowed_prefix)):
        raise ValueError(
            f"Path traversal detected: '{file_url}' resolves to '{candidate}' "
            f"which is outside the allowed storage root '{_ALLOWED_UPLOADS}'"
        )
    return candidate
