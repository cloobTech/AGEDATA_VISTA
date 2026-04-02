from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.utils.get_db_session import get_db_session
from models.user import User
from services.auth.jwt import verify_access_token
from storage import db

# Keep the OAuth2PasswordBearer for Swagger UI / API clients that send Bearer
outh2_scheme = OAuth2PasswordBearer(tokenUrl='login', auto_error=False)

COOKIE_NAME = "access_token"


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    bearer_token: str | None = Depends(outh2_scheme),
) -> User:
    """Get the currently authenticated user.

    Token resolution order:
    1. httpOnly cookie ``access_token`` (set by login/logout endpoints)
    2. ``Authorization: Bearer <token>`` header (Swagger UI / legacy clients)

    This dual-source approach allows a zero-downtime migration: existing API
    clients using Bearer tokens continue to work while new browser sessions
    use the more secure httpOnly cookie.
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate user credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Prefer httpOnly cookie
    token: str | None = request.cookies.get(COOKIE_NAME)

    # 2. Fall back to Authorization header
    if not token:
        token = bearer_token

    if not token:
        raise credential_exception

    payload: dict = verify_access_token(token, credential_exception)
    current_user = await db.get(session, User, payload["user_id"])
    if current_user is None:
        raise credential_exception
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This user has been disabled",
        )
    return current_user
