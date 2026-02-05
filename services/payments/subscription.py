from datetime import datetime, timedelta, timezone
from storage import db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.default_response import DefaultResponse
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.subscription import Subscription, SubscriptionStatus
from models.subscription_plan import Plan
from models.user import User
import hashlib
import hmac
from settings.pydantic_config import settings
import httpx
from services.payments.plan import get_trial_plan


EXCLUDE_OBJ = ['_class_', 'subscription_plan']


async def create_trial_subscription(user_id: str, session: AsyncSession):
    plan: Plan = await get_trial_plan(session)
    start_date = datetime.now(timezone.utc)
    end_date = start_date + timedelta(days=plan.duration_days)
    trial_sub = Subscription(
        plan_id=plan.id,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date

    )
    return trial_sub


async def create_subscription(subscription_data: dict, session: AsyncSession):
    try:
        if not subscription_data:
            raise DataRequiredError(
                "Must provide data to create a subscription")

        user_id = subscription_data.get("user_id")
        plan_id = subscription_data.get("plan_id")

        if not user_id or not plan_id:
            raise DataRequiredError("Both user_id and plan_id are required")

        user = await db.get(session, User, user_id)
        if not user:
            raise EntityNotFoundError("User not found")

        plan = await db.get(session, Plan, plan_id)
        if not plan:
            raise EntityNotFoundError("Plan not found")

        # Expire old sub
        active_sub = await db.filter(
            session,
            Subscription,
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE.value,
            fetch_one=True
        )
        if active_sub:
            active_sub.status = SubscriptionStatus.EXPIRED.value
            active_sub.end_date = datetime.now(timezone.utc)
            session.add(active_sub)

        # New sub
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=plan.duration_days)

        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            start_date=start_date,
            end_date=end_date,
            status=SubscriptionStatus.ACTIVE.value,
            payment_info=subscription_data.get("payment_info", {})
        )

        await subscription.save(session)

        return subscription.to_dict()

    except Exception as e:
        raise ValueError(f"Failed to create subscription: {str(e)}")


async def get_user_active_subscription(user_id: str, session: AsyncSession):
    if not user_id:
        raise DataRequiredError("user_id is required")

    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")

    subscription = await db.filter(
        session,
        Subscription,
        Subscription.user_id == user_id,
        Subscription.status == SubscriptionStatus.ACTIVE.value,
        fetch_one=True
    )

    if not subscription:
        raise EntityNotFoundError("No active subscription found for this user")

    sub_dict = subscription.to_dict(exclude=EXCLUDE_OBJ)
    # Load plan relationship
    sub_dict['plan'] = subscription.subscription_plan.to_dict(
        exclude=EXCLUDE_OBJ) if subscription.subscription_plan else None

    return DefaultResponse(
        status="success",
        message="Active subscription retrieved successfully",
        data=sub_dict
    )


async def list_user_subscriptions(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")

    subscriptions = await db.filter(
        session,
        Subscription,
        Subscription.user_id == user_id
    )

    if not subscriptions:
        return DefaultResponse(
            status="success",
            message="No subscriptions found for this user",
            data=[]
        )

    sub_list = [sub.to_dict(EXCLUDE_OBJ) for sub in subscriptions]
    for i, sub in enumerate(subscriptions):
        sub_list[i]['plan'] = sub.subscription_plan.to_dict(EXCLUDE_OBJ
                                                            ) if sub.subscription_plan else None

    return DefaultResponse(
        status="success",
        message="Subscriptions retrieved successfully",
        data=sub_list if sub_list else []
    )


async def has_active_subscription(user_id: str, session: AsyncSession) -> bool:
    sub = await db.filter(
        session,
        Subscription,
        Subscription.user_id == user_id,
        Subscription.status == "active",
        fetch_one=True
    )
    return sub is not None


def verify_payment_signature(request_body: bytes, received_signature: str) -> bool:
    """
    Verify Paystack signature to ensure the request is from Paystack.
    """
    signature = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode(),
        msg=request_body,
        digestmod=hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(signature, received_signature)


async def initialize_payment(user: User, plan_id: str, session: AsyncSession, renewal: bool = False):
    plan = await db.get(session, Plan, plan_id)
    if not plan:
        raise EntityNotFoundError("Plan not found")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        payload = {
            "email": user.email,
            "amount": int(plan.price * 100),
            "metadata": {
                "user_id": user.id,
                "plan_id": plan.id,
                "renewal": renewal,
            }
        }
        resp = await client.post(
            f"{settings.PAYSTACK_BASE_URL}/transaction/initialize",
            headers=headers,
            json=payload
        )
        result = resp.json()

    if not result.get("status"):
        raise ValueError("Failed to initialize payment")

    return {
        "authorization_url": result["data"]["authorization_url"],
        "reference": result["data"]["reference"]
    }


async def renew_subscription(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")

    active_sub = await db.filter(
        session,
        Subscription,
        Subscription.user_id == user_id,
        Subscription.status == "active",
        fetch_one=True
    )
    if not active_sub:
        raise EntityNotFoundError("No active subscription found to renew")

    # Just trigger a new payment for renewal
    return await initialize_payment(user, active_sub.plan_id, session=session, renewal=True)


async def paystack_webhook(request, session: AsyncSession):
    request_body = await request.body()
    signature_header = request.headers.get("x-paystack-signature")

    if not signature_header or not verify_payment_signature(request_body, signature_header):
        raise ValueError("Invalid or missing Paystack signature")

    payload = await request.json()
    event = payload.get("event")
    data = payload.get("data", {})

    if event != "charge.success":
        return {"status": "ignored", "message": "Event not processed"}

    reference = data.get("reference")

    # Verify payment with Paystack
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        resp = await client.get(
            f"{settings.PAYSTACK_BASE_URL}/transaction/verify/{reference}",
            headers=headers
        )
        result = resp.json()

    if not (result.get("status") and result.get("data", {}).get("status") == "success"):
        raise ValueError("Payment verification failed")

    metadata = result["data"].get("metadata", {})
    user_id = metadata.get("user_id")
    plan_id = metadata.get("plan_id")
    renewal = metadata.get("renewal", False)
    payment_info = {
        "paystack_reference": reference,
        "amount": result["data"].get("amount") / 100,
        "paid_at": result["data"].get("paid_at"),
        "channel": result["data"].get("channel"),
        "currency": result["data"].get("currency"),
    }

    # 🔑 Create subscription (works for both new + renewal)
    subscription = await create_subscription(
        {"user_id": user_id, "plan_id": plan_id, "payment_info": payment_info},
        session
    )

    return DefaultResponse(
        status="success",
        message="Subscription created via Paystack webhook",
        data={
            "subscription": subscription,
            "renewal": renewal
        }
    )
