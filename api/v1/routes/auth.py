import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import InvalidRequestError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth.google import google_auth
from services.auth.local_auth import (
    login_user, register_user, verify_email, request_reset_token, reset_password)
from errors.exceptions import (
    UserDisabledError, EmailNotVerifiedError, UserAlreadyExistsError,
    InvalidTokenError, TokenExpiredError,
)
from schemas.auth import RegisterUser, TokenResponse, VerifyEmailTokenInput, RequestResetToken, updatePassword
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user, COOKIE_NAME
from api.v1.limiter import limiter
from models.user import User

router = APIRouter(tags=['Authentication'], prefix='/api/v1/auth')

# Whether to use Secure flag on the cookie — always True in production.
_IS_PROD = os.environ.get("DEV_ENV", "development").lower() == "production"

_COOKIE_KWARGS = dict(
    key=COOKIE_NAME,
    httponly=True,
    secure=_IS_PROD,
    samesite="lax",   # "strict" breaks OAuth redirect flows; "lax" is a safe default
    max_age=60 * int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
    path="/",
)


def _set_auth_cookie(response: Response, token_data: dict) -> None:
    """Set the httpOnly auth cookie from a token response dict."""
    access_token = token_data.get("access_token", "")
    if access_token:
        response.set_cookie(value=access_token, **_COOKIE_KWARGS)


@router.post('/google-auth', response_model=TokenResponse)
async def google_auth_route(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
):
    """Authenticate via Google OAuth. Sets httpOnly auth cookie."""
    token_data = await google_auth(request, session)
    _set_auth_cookie(response, token_data if isinstance(token_data, dict) else token_data.model_dump())
    return token_data


@router.post('/login', status_code=status.HTTP_200_OK, response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    storage: AsyncSession = Depends(get_db_session),
):
    """Log in a user. Sets httpOnly auth cookie."""
    try:
        token_dict: TokenResponse = await login_user(user_credentials, storage)
        token_payload = token_dict if isinstance(token_dict, dict) else token_dict.model_dump()
        _set_auth_cookie(response, token_payload)
        return token_dict
    except (InvalidRequestError, NoResultFound) as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Email or Password") from e
    except UserDisabledError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except EmailNotVerifiedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=DefaultResponse)
@limiter.limit("3/minute")
async def register_new_user(
    request: Request,
    data: RegisterUser,
    background_task: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
):
    """Register a new user."""
    try:
        response = await register_user(data, session, background_task)
        return response
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists") from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.post('/verify-email', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def verify_email_route(
    token_input: VerifyEmailTokenInput,
    response: Response,
    storage: AsyncSession = Depends(get_db_session),
):
    """Verify a user's email. Sets httpOnly auth cookie on success."""
    try:
        token_response = await verify_email(token_input, storage)
        token_payload = token_response if isinstance(token_response, dict) else token_response.model_dump()
        _set_auth_cookie(response, token_payload)
        return token_response
    except TokenExpiredError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired") from e
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.post('/logout', status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """Clear the httpOnly auth cookie (logout)."""
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"status": "success", "message": "Logged out successfully"}


@router.get('/me', status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile.

    Called by the frontend after login to retrieve user_id and display data
    without having to decode the JWT from JavaScript (which is impossible
    with httpOnly cookies).
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "corporate_name": getattr(current_user, "corporate_name", None),
        "profile_picture": getattr(current_user, "profile_picture", None),
        "plan": getattr(current_user, "plan", None),
        "email_verified": current_user.email_verified,
        "disabled": current_user.disabled,
    }


@router.post('/request-reset-token', status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def request_token(
    request: Request,
    data: RequestResetToken,
    background_task: BackgroundTasks,
    storage: AsyncSession = Depends(get_db_session),
):
    """Request a password reset token."""
    try:
        response = await request_reset_token(data, storage, background_task)
        return response
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e


@router.put('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password_route(
    data: updatePassword,
    storage: AsyncSession = Depends(get_db_session),
):
    """Reset a user's password."""
    try:
        response = await reset_password(data, storage)
        return response
    except TokenExpiredError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired") from e
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") from e
