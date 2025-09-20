from storage import db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.default_response import DefaultResponse
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.subscription import Subscription
from models.subscription_plan import Plan


async def get_all_plans(session: AsyncSession):
    plans = await db.all(session, Plan)
    if not plans:
        return DefaultResponse(
            status="success",
            message="No plans found",
            data=[]
        )
    plan_data = [plan.to_dict() for plan in plans.values()]
    return DefaultResponse(
        status="success",
        message="Plans found",
        data=plan_data
    )


async def get_plan_by_id(plan_id: str, session: AsyncSession):
    plan = await db.get(session, Plan, plan_id)
    if not plan:
        raise EntityNotFoundError("Plan not found")
    return DefaultResponse(
        status="success",
        message="Plan found",
        data=plan.to_dict()
    )



async def create_plan(plan_data: dict, session: AsyncSession):
    if not plan_data:
        raise DataRequiredError("Must provide data to create a plan")
    plan = Plan(**plan_data)
    await plan.save(session)
    return DefaultResponse(
        status="success",
        message="Plan created successfully",
        data=plan.to_dict()
    )


async def update_plan(plan_id: str, plan_data: dict, session: AsyncSession):
    plan = await db.get(session, Plan, plan_id)
    if not plan:
        raise EntityNotFoundError("Plan not found")
    if not plan_data:
        raise DataRequiredError("Must provide data to update")
    await plan.update(session, plan_data)
    return DefaultResponse(
        status="success",
        message="Plan updated successfully",
        data=plan.to_dict()
    )



async def delete_plan(plan_id: str, session: AsyncSession):
    plan = await db.get(session, Plan, plan_id)
    if not plan:
        raise EntityNotFoundError("Plan not found")
    # Check if any subscriptions are associated with this plan
    subscriptions = await db.filter_by(session, Subscription, plan_id=plan_id)
    if subscriptions:
        raise DataRequiredError("Cannot delete plan with active subscriptions")
    await plan.delete(session)
    return DefaultResponse(
        status="success",
        message="Plan deleted successfully",
        data=None
    )
