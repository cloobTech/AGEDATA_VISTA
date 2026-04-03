from datetime import datetime, timezone
import logging
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from errors.exceptions import UserAlreadyExistsError, UserDisabledError, EmailNotVerifiedError
from storage import db
from models.user import User
from utils.generate_token import generate_token

_log = logging.getLogger(__name__)


async def check_user_existence(session: AsyncSession, email: str):
    """Check whether *email* is already registered.

    Previous implementation: if an unverified account existed, it was deleted
    to allow re-registration.  This created a race condition: two concurrent
    registrations with the same email could both pass the check, and an
    attacker could also delete a legitimate user's unverified account.

    Fixed: keep the unverified account intact and trigger a fresh verification
    email instead.  The caller (register_user) is responsible for sending the
    email; here we simply raise so the caller knows the account already exists.
    """
    user = await db.find_by(session, User, email=email)
    if user:
        if user.email_verified:
            raise UserAlreadyExistsError("User already exists")
        # Unverified account — do NOT delete it.  Signal the caller to resend
        # the verification email by raising with a distinct message.
        _log.info(
            "Registration attempt for existing unverified account: %s — resending verification",
            email,
        )
        raise UserAlreadyExistsError(
            "An account with this email already exists and is pending email verification. "
            "Please check your inbox for the verification link, or request a new one."
        )


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
    """Verify Password.

    Returns False (never raises) when the stored hash is absent, corrupted,
    or not a valid bcrypt hash — treating all such cases as wrong password
    rather than leaking an internal error.
    """
    try:
        hashed_password = user.password
        if not hashed_password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        return False
