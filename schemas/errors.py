"""Structured error response schema — Phase 9A.

Using a typed Pydantic model instead of ad-hoc dicts ensures that every
error response from the API has a consistent shape that the frontend can
rely on.  FastAPI's exception handlers return this model when raising
HTTPException or application-level errors.

Fields
------
detail  The human-readable error message (required).
code    An optional machine-readable error code for programmatic handling.
        Examples: "NOT_FOUND", "RATE_LIMITED", "INVALID_INPUT".
"""
from typing import Optional
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Structured error response returned by all error handlers."""
    detail: str
    code:   Optional[str] = None
