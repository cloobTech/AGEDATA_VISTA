from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.v1.utils.get_db_session import get_db_session
from models.user import User
from services.auth.jwt import verify_access_token
from storage import db


outh2_scheme = OAuth2PasswordBearer(tokenUrl='login')


async def get_current_user(
    session: AsyncSession = Depends(get_db_session),  # 👈 here!
    token: str = Depends(outh2_scheme)
) -> User:
    """Get Current Logged in User"""

    credential_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate User token", headers={"WWW-Authenticate": "Bearer"})
    payload: dict = verify_access_token(token, credential_exceptions)
    current_user = await db.get(session, User, payload["user_id"])
    if not current_user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email not verified")
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="This User has been disabled")
    return current_user
