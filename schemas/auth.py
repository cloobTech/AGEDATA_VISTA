from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token Response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
