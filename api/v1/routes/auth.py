from fastapi import APIRouter, Depends,  HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import InvalidRequestError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth.local_auth import (
    login_user, register_user, verify_email, request_reset_token, reset_password)
from errors.exceptions import UserDisabledError, EmailNotVerifiedError, UserAlreadyExistsError, InvalidTokenError, TokenExpiredError
from schemas.auth import RegisterUser,  TokenResponse, VerifyEmailTokenInput, RequestResetToken, updatePassword
from schemas.default_response import DefaultResponse
from api.v1.utils.get_db_session import get_db_session


router = APIRouter(tags=['Authentication'], prefix='/api/v1/auth')


@router.post('/login', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), storage: AsyncSession = Depends(get_db_session)):
    """Handle Logging in a user"""

    try:
        token_dict: TokenResponse = await login_user(user_credentials, storage)
        return token_dict
    except InvalidRequestError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except UserDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except EmailNotVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e




@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=DefaultResponse)
async def register_new_user(data: RegisterUser, background_task: BackgroundTasks, session: AsyncSession = Depends(get_db_session)):
    """Register a new user"""
    try:
        response = await register_user(data, session, background_task)
        return response
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists") from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/verify-email', status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def verify_email_route(token_input: VerifyEmailTokenInput, storage: AsyncSession = Depends(get_db_session)):
    """Verify a user's email"""
    try:
        response = await verify_email(token_input, storage)
        return response
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired") from e
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post('/request-reset-token', status_code=status.HTTP_200_OK)
async def request_token(data: RequestResetToken, background_task: BackgroundTasks, storage: AsyncSession = Depends(get_db_session)):
    """Request a reset token"""
    try:
        response = await request_reset_token(data, storage, background_task)
        return response
    except NoResultFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.put('/reset-password', status_code=status.HTTP_200_OK)
async def reset_password_route(data: updatePassword, storage: AsyncSession = Depends(get_db_session)):
    """This route can be used to reset a user's password & (forgot password)"""
    try:
        response = await reset_password(data, storage)
        return response
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token Expired") from e
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Token") from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e