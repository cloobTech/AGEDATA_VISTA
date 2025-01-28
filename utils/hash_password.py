import bcrypt

# hash password


def hash_password(password: str) -> str:
    """ hash password """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
