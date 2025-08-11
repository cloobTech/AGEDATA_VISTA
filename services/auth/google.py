from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, HTTPException
import httpx
from services.users.helpers import get_user_by_email, check_user_status, create_user
from services.auth.jwt import return_access_and_refesh_tokens


async def google_auth(request: Request, session: AsyncSession):
    """
    Authenticate a user via Google credential response from @react-oauth/google.
    The frontend should send the credential in the request body as:
    {
        "credential": "<GOOGLE_ID_TOKEN>"
    }
    """
    # Step 0: Get the credential from request body
    try:
        data = await request.json()
        credential = data.get("credential")
        if not credential:
            raise HTTPException(status_code=400, detail="Missing Google credential")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request format")

    try:
        # Step 1: Verify token with Google
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
            )
            resp.raise_for_status()
            google_user_data = resp.json()

        email = google_user_data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google account does not provide an email")

        # Step 2: Check if user exists
        user = await get_user_by_email(email, session)
        if user:
            check_user_status(user, check_password=False)
            return return_access_and_refesh_tokens(user)

        # Step 3: Create a new user if not found
        user_data = {
            "email": email,
            "password": None,  # No password for Google auth
            "first_name": google_user_data.get("given_name", ""),
            "last_name": google_user_data.get("family_name", ""),
            "corporate_name": None,
            "email_verified": google_user_data.get("email_verified", False),
            "reset_token": None
        }

        new_user = await create_user(user_data, session)
        return return_access_and_refesh_tokens(new_user)

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Google token verification failed: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")