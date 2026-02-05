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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from errors.exceptions import InvalidTokenError, TokenExpiredError
from models.user import User
from schemas.auth import RegisterUser, RequestResetToken, TokenResponse, VerifyEmailTokenInput, updatePassword
from schemas.default_response import DefaultResponse
from settings.pydantic_config import settings
from storage import db
from utils.generate_token import generate_token
from utils.email_service import send_email
from services.users.helpers import (
    get_user_by_email, check_user_status, verify_password, check_user_existence, create_user)
from services.auth.jwt import return_access_and_refesh_tokens
from services.payments.subscription import create_trial_subscription


async def login_user(form_data, session: AsyncSession) -> TokenResponse:
    """Login a user"""
    email = form_data.username
    password = form_data.password
    user = await get_user_by_email(email, session)
    check_user_status(user)
    if not verify_password(user, password):
        raise InvalidRequestError("Invalid Email or Password")
    token = return_access_and_refesh_tokens(user)

    return token


async def register_user(data: RegisterUser, session: AsyncSession, background_email_service) -> DefaultResponse:
    """Register a new user"""
    user_auth_details = data.model_dump()

    # Check if user already exists
    await check_user_existence(session, user_auth_details.get('email'))
    new_user = create_user(user_auth_details)

    # create trial subscription
    trial_sub = await create_trial_subscription(new_user.id, session=session)

    # Send verification email
    # Schedule the email sending task

    background_email_service.add_task(send_email, new_user.email, "Verify your email",
                                      "verification_email.html", {"verification_token": new_user.reset_token})

    db.add_all(session, [new_user, trial_sub])

    await db.save(session)

    return DefaultResponse(
        status="success",
        message="User registered successfully, kindly verify your email",
        data={"user": new_user.to_dict(), "subscription": trial_sub.to_dict()})


async def verify_email(token_input: VerifyEmailTokenInput, session: AsyncSession) -> TokenResponse:
    """Verify a user's email"""
    token_data = token_input.model_dump()
    token = token_data.get('token')

    user = await db.find_by(session, User, reset_token=token)
    if not user:
        raise InvalidTokenError("Invalid Token")
    # token is valid for 3 minutes
    if datetime.now(timezone.utc) - user.token_created_at.replace(tzinfo=timezone.utc) > timedelta(minutes=3):
        raise TokenExpiredError("Token Expired")

    # update user email_verified status
    await user.update(session, {"email_verified": True, "reset_token": ""})

    token: TokenResponse = return_access_and_refesh_tokens(user)
    return token


async def request_reset_token(data: RequestResetToken, session: AsyncSession, background_email_service) -> DefaultResponse:
    """Request a reset token"""
    data = data.model_dump()
    email = data.get('email')
    user = await db.find_by(session, User, email=email)
    if not user:
        raise NoResultFound("User Not Found!")

    # Save the token in your database
    await user.update(session, {"reset_token": generate_token(), "token_created_at": datetime.now(timezone.utc)})

    # Send verification email
    if settings.DEV_ENV == "production":
        background_email_service.add_task(send_email, user.email, "Reset Token",
                                          "reset_token.html", {"reset_token": user.reset_token})

    return DefaultResponse(
        status="success",
        message="Token sent to mail successfully"
    )


async def reset_password(data: updatePassword, session: AsyncSession) -> DefaultResponse:
    """Reset a user's password"""
    data = data.model_dump()
    token = data.get('token')  # otp
    password = data['meta'].get('password')

    user = await db.find_by(session, User, reset_token=token)
    if not user:
        raise InvalidTokenError("Invalid Token")
    # # tokens valid for 3 minutes
    if datetime.now(timezone.utc) - user.token_created_at.replace(tzinfo=timezone.utc) > timedelta(minutes=3):
        raise TokenExpiredError("Token Expired")

    # Update User with hashed password and reset token
    hashed_pwd = bcrypt.hashpw(password.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    await user.update(session, {"password": hashed_pwd, "reset_token": ""})

    return DefaultResponse(
        status="success",
        message="Password Reset Successful",
    )
