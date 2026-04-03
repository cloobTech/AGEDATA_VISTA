"""
google.py — Google OAuth 2.0 authentication service.

Uses google-auth to verify the ID token against Google's JWKS endpoint,
which is the cryptographically secure approach.

Previous implementation: sent the token to Google's tokeninfo endpoint over
HTTP.  That approach does NOT verify the JWT signature client-side — it relies
entirely on Google's server, is vulnerable to TOCTOU attacks in some edge
cases, and leaks the raw credential over a network hop.

Current implementation:
- Verifies the JWT signature locally using Google's public keys (JWKS)
- Checks audience (must match GOOGLE_CLIENT_ID) and issuer automatically
- All done synchronously in a threadpool since google-auth is sync-only
"""

import os
import asyncio
from functools import partial

from fastapi import HTTPException, Request
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession

from services.users.helpers import get_user_by_email, check_user_status, create_user
from services.auth.jwt import return_access_and_refesh_tokens
from services.payments.subscription import create_trial_subscription
from settings.pydantic_config import settings
from storage import db

# Cache a single Google Request object — it manages JWKS caching internally
_GOOGLE_REQUEST = google_requests.Request()


def _verify_google_token_sync(token: str) -> dict:
    """Verify a Google ID token synchronously (runs in threadpool).

    Raises:
        ValueError: if the token is invalid, expired, or has the wrong audience.
    """
    return id_token.verify_oauth2_token(
        token,
        _GOOGLE_REQUEST,
        settings.GOOGLE_CLIENT_ID,
    )


async def google_auth(request: Request, session: AsyncSession):
    """Authenticate a user via Google ID token.

    The frontend sends the raw credential returned by @react-oauth/google in
    the request body as ``{"credential": "<ID_TOKEN>"}``.

    The token is verified locally against Google's JWKS — no additional HTTP
    call to tokeninfo is made, making this immune to network-level MITM on the
    verification step.
    """
    # Parse the credential from the request body
    try:
        data = await request.json()
        credential = data.get("credential")
        if not credential:
            raise HTTPException(status_code=400, detail="Missing Google credential")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request format")

    # Verify the token in a threadpool (google-auth is blocking I/O)
    try:
        loop = asyncio.get_running_loop()
        google_user_data = await loop.run_in_executor(
            None,
            partial(_verify_google_token_sync, credential),
        )
    except ValueError as exc:
        # google-auth raises ValueError for invalid/expired tokens
        raise HTTPException(
            status_code=401,
            detail=f"Invalid Google token: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Google token verification failed: {exc}",
        ) from exc

    email = google_user_data.get("email")
    if not email:
        raise HTTPException(
            status_code=400, detail="Google account does not provide an email"
        )

    # Check for existing user or create a new one
    try:
        user = await get_user_by_email(email, session)
    except Exception:
        user = None

    if user:
        check_user_status(user, check_password=False)
        return return_access_and_refesh_tokens(user)

    # New user — create account (email already verified by Google)
    user_data = {
        "email": email,
        "password": None,
        "first_name": google_user_data.get("given_name", ""),
        "last_name": google_user_data.get("family_name", ""),
        "corporate_name": None,
        "email_verified": True,
        "reset_token": None,
    }
    new_user = create_user(user_data)
    trial_sub = await create_trial_subscription(new_user.id, session=session)
    db.add_all(session, [new_user, trial_sub])
    await db.save(session)
    return return_access_and_refesh_tokens(new_user)
