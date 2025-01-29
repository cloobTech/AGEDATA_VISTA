from pydantic import BaseModel


class DefaultResponse(BaseModel):
    """Default response schema"""
    status: str
    message: str
    data: dict | list = None
