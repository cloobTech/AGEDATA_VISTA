class UserDisabledError(Exception):
    """Raised when the user is disabled"""
    pass


class EmailNotVerifiedError(Exception):
    """Raised when the user's email is not verified"""
    pass


class UserAlreadyExistsError(Exception):
    """Raised when the user already exists"""
    pass


class TokenExpiredError(Exception):
    """Raised when the token has expired"""
    pass


class InvalidTokenError(Exception):
    """Raised when the token is invalid"""
    pass


class EntityNotFoundError(Exception):
    """Missing entity from db"""
    pass


class DataRequiredError(Exception):
    """Raised when data is required"""
    pass


class AppointmentSlotNotAvailableError(Exception):
    """Raised when the appointment slot is not available"""
    pass


class InvalidFileError(Exception):
    """Raised when the file is invalid"""
    pass
