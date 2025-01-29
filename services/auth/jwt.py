from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from settings.pydantic_config import settings
from schemas.auth import TokenResponse


def create_access_token(data: dict) -> str:
    """Create A New Jwt Access Token"""
    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM)  # returns a token
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create A New Jwt Refresh Token"""
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + \
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM)  # returns a token
    return encoded_jwt


def verify_access_token(token: str, credential_exceptions: Exception) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        if payload is None:
            raise credential_exceptions
        return payload

    except JWTError as exc:
        raise credential_exceptions from exc


def create_refresh_tokens(refresh_token: str, credential_exceptions) -> TokenResponse:
    """Create a new access token and refresh token"""
    payload = verify_access_token(
        refresh_token, credential_exceptions)
    new_access_token = create_access_token(payload)
    new_refresh_token = create_refresh_token(payload)
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token, token_type="Bearer")


def return_access_and_refesh_tokens(user) -> TokenResponse:
    """Return Access and Refresh Tokens"""
    data = {"user_id": user.id,
            "user_role": user.role,
            }
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")
