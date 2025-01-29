#!/usr/bin/python3
"""Modules to take care of secondary auth functions
    - Register User
    - Verify Email
    - Request Token
    - Reset Password
    - Change Password (Same as reset pwd)
"""

from datetime import datetime, timedelta, timezone
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from errors.exceptions import InvalidTokenError, TokenExpiredError
from models.user import User
from schemas.auth import RegisterUser, RequestResetToken, TokenResponse, VerifyEmailTokenInput
from schemas.default_response import DefaultResponse
from settings.pydantic_config import settings
from services.users.helpers import check_user_existence, create_user
from storage.database import DBStorage
from utils.generate_token import generate_token
from utils.email_service import send_email
from services.users.helpers import get_user_by_email, check_user_status, verify_password
from services.auth.jwt import return_access_and_refesh_tokens


async def login_user(form_data, storage: DBStorage) -> TokenResponse:
    """Login a user"""
    email = form_data.username
    password = form_data.password
    user = await get_user_by_email(email, storage)
    check_user_status(user)
    if not verify_password(user, password):
        raise InvalidRequestError("Invalid Email or Password")
    token = return_access_and_refesh_tokens(user)

    return token


async def register_user(data: RegisterUser, storage: DBStorage, background_email_service) -> DefaultResponse:
    """Register a new user"""
    user_auth_details = data.model_dump()

    # Check if user already exists
    await check_user_existence(storage, user_auth_details.get('email'))
    new_user = create_user(user_auth_details)

    # Send verification email
    # Schedule the email sending task
    if settings.DEV_ENV == "production":
        background_email_service.add_task(send_email, new_user.email, "Verify your email",
                                          "email_verification.html", {"verification_token": new_user.reset_token})

    await new_user.save()

    return DefaultResponse(
        status="success",
        message="User registered successfully, kindly verify your email",
        data=new_user.to_dict())


async def verify_email(token_input: VerifyEmailTokenInput, storage: DBStorage) -> TokenResponse:
    """Verify a user's email"""
    token_data = token_input.model_dump()
    token = token_data.get('token')

    user = await storage.find_by(User, reset_token=token)
    if not user:
        raise InvalidTokenError("Invalid Token")
    # token is valid for 3 minutes
    if datetime.now(timezone.utc) - user.token_created_at.replace(tzinfo=timezone.utc) > timedelta(minutes=3):
        raise TokenExpiredError("Token Expired")

    # merge the current session object
    await storage.merge(user)

    # update user email_verified status
    await user.update({"email_verified": True, "reset_token": ""})

    token: TokenResponse = return_access_and_refesh_tokens(user)
    return token


async def request_reset_token(data: RequestResetToken, storage: DBStorage, background_email_service) -> DefaultResponse:
    """Request a reset token"""
    data = data.model_dump()
    email = data.get('email')
    user = await storage.find_by(User, email=email)
    if not user:
        raise NoResultFound("User Not Found!")
    await storage.merge(user)

    # Save the token in your database
    await user.update({"reset_token": generate_token(), "token_created_at": datetime.now(timezone.utc)})

    # Send verification email
    if settings.DEV_ENV == "production":
        background_email_service.add_task(send_email, user.email, "Token",
                                          "email_verification.html", {"verification_token": user.reset_token})

    return DefaultResponse(
        status="success",
        message="Token sent successfully"
    )


async def reset_password(data: VerifyEmailTokenInput, storage: DBStorage) -> DefaultResponse:
    """Reset a user's password"""
    data = data.model_dump()
    token = data.get('token')  # otp
    password = data['meta'].get('password')

    user = await storage.find_by(User, reset_token=token)
    if not user:
        raise InvalidTokenError("Invalid Token")
    # # tokens valid for 3 minutes
    if datetime.now(timezone.utc) - user.token_created_at.replace(tzinfo=timezone.utc) > timedelta(minutes=3):
        raise TokenExpiredError("Token Expired")

    await storage.merge(user)

    # Update User with hashed password and reset token
    hashed_pwd = bcrypt.hashpw(password.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    await user.update({"password": hashed_pwd, "reset_token": ""})

    return DefaultResponse(
        status="success",
        message="Password Reset Successful",
    )
