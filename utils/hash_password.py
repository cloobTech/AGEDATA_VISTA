import bcrypt
from settings.pydantic_config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with the configured work factor.

    The work factor (BCRYPT_ROUNDS) defaults to 14 and is configurable via
    the BCRYPT_ROUNDS environment variable.  Higher values increase brute-force
    resistance at the cost of CPU time per login.
    """
    rounds = settings.BCRYPT_ROUNDS
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
