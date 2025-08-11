from datetime import datetime, timezone
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from errors.exceptions import UserAlreadyExistsError, UserDisabledError, EmailNotVerifiedError
from storage import db
from models.user import User
from utils.generate_token import generate_token


async def check_user_existence(session: AsyncSession, email: str):
    """Check if a user already exists"""
    user = await db.find_by(session, User, email=email)
    if user:
        if not user.email_verified:
            await user.delete(session)
        else:
            raise UserAlreadyExistsError("User already exists")


def create_user(user_auth_details: dict) -> User:
    """Create a new user"""
    new_user = User(**user_auth_details)
    new_user.reset_token = generate_token()
    new_user.token_created_at = datetime.now(timezone.utc)
    return new_user


async def get_user_by_email(email: str, session: AsyncSession) -> User:
    """Get a user by email"""
    try:
        user = await db.find_by(session, User, email=email)
        if user is None:
            raise NoResultFound("User Not Found!")
        return user
    except NoResultFound as exc:
        raise InvalidRequestError("Invalid Email or Password") from exc


def check_user_status(user: User, check_password: bool = True):
    """Check User Status"""
    if not user.password and check_password:
        raise NoResultFound("Password Field Empty!")
    if user.disabled:
        raise UserDisabledError("User is Disabled")
    if not user.email_verified:
        raise EmailNotVerifiedError("Email Not Verified")


def verify_password(user: User, password: str | bytes) -> bool:
    """Verify Password"""
    hashed_password = user.password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
