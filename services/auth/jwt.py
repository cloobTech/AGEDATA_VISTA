from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from sqlalchemy.exc import InvalidRequestError
from settings.pydantic_config import settings
from storage.database import DBStorage
from schemas.auth import TokenResponse
# from services.users.user_management import get_user_by_email, check_user_status, verify_password


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


# async def valid_login(email: str, password: str | bytes, storage: AsyncSession) -> TokenResponse:
#     """Validate a user's credentials"""
#     user = await get_user_by_email(email, storage)
#     check_user_status(user)
#     if not verify_password(user, password):
#         raise InvalidRequestError("Invalid Email or Password")
#     data_to_encode = {"user_id": user.id,
#                       "user_type": user.user_type,
#                       "profile_id": user.user_profile_id}
#     token = create_access_token(data_to_encode)
#     refresh_token = create_refresh_token(data_to_encode)
#     return TokenResponse(access_token=token, refresh_token=refresh_token, token_type="Bearer")
