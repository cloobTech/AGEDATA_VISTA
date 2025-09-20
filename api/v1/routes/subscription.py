from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from schemas.payment import SubscriptionInit
from api.v1.utils.get_db_session import get_db_session
from api.v1.utils.current_user import get_current_user
from models.user import User
from services.payments.subscription import (
    create_subscription,
    get_user_active_subscription,
    list_user_subscriptions,
    has_active_subscription,
    renew_subscription,
    paystack_webhook,
    initialize_payment,
)

router = APIRouter(tags=["Subscriptions"], prefix="/api/v1/subscriptions")


@router.post("/initialize", status_code=status.HTTP_200_OK)
async def initialize_subscription(
    subscription_init: SubscriptionInit,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Initialize a new subscription payment (returns Paystack checkout link)"""
    try:

        plan_id = subscription_init.plan_id
        return await initialize_payment(current_user, plan_id, session=session, renewal=False)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# @router.post("/", status_code=status.HTTP_201_CREATED)
# async def create_subscription_route(
#     subscription_data: dict,
#     session: AsyncSession = Depends(get_db_session),
#     current_user: User = Depends(get_current_user),
# ):
#     """Create a new subscription (should normally be triggered by webhook)"""
#     try:
#         response = await create_subscription(subscription_data, session)
#         return response
#     except (DataRequiredError, EntityNotFoundError) as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )


@router.get("/active", status_code=status.HTTP_200_OK)
async def get_active_subscription(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Get the user's active subscription"""
    try:
        return await get_user_active_subscription(current_user.id, session)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def list_subscriptions(
    user_id: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """List all subscriptions for the current user"""
    return await list_user_subscriptions(user_id, session)


@router.get("/has-active", status_code=status.HTTP_200_OK)
async def check_active_subscription(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Check if user has an active subscription (boolean)"""
    has_sub = await has_active_subscription(current_user.id, session)
    return {"has_active_subscription": has_sub}


@router.post("/renew", status_code=status.HTTP_200_OK)
async def renew_user_subscription(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Renew an active subscription (kicks off Paystack payment)"""
    try:
        return await renew_subscription(current_user.id, session)
    except EntityNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def paystack_webhook_route(
    request: Request, session: AsyncSession = Depends(get_db_session)
):
    """Paystack webhook for payment confirmation"""
    try:
        return await paystack_webhook(request, session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
