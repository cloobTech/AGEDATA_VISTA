from pydantic import BaseModel, EmailStr


class RegisterUser(BaseModel):
    """Register User"""
    email: str
    password: str
    first_name: str
    last_name: str
    corporate_name: str | None = None
    email_verified: bool = False
    reset_token: str | None = None


class TokenResponse(BaseModel):
    """Token Response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class VerifyEmailTokenInput(BaseModel):
    """Verify Email Token Input"""
    token: str


class RequestResetToken(BaseModel):
    """Request Reset Token"""
    email: EmailStr
