from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError,  DataRequiredError
from storage import db
from schemas.default_response import DefaultResponse
from models.user import User


async def get_all_users(session: AsyncSession):
    users = await db.all(session, User)
    if not users:
        return DefaultResponse(
            status="success",
            message="No users found",
            data=[]
        )
    user_data = [user.to_dict() for user in users.values()]
    return DefaultResponse(
        status="success",
        message="Users found",
        data=user_data
    )


async def get_user_by_id(user_id: str, params: str, session: AsyncSession):
    param_list = [param.strip() for param in params.split(",")] if params else None
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if param_list:
        for relationship in param_list:
            try:
                await getattr(user.awaitable_attrs, relationship)
            except AttributeError:
                pass
    return DefaultResponse(
        status="success",
        message="User found",
        data=user.to_dict(include=param_list)
    )


async def update_user(user_id: str, user_data: dict, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if not user_data:
        raise DataRequiredError("Must provide data to update")
    await user.update(session, user_data)
    await user.save(session)
    return DefaultResponse(
        status="success",
        message="User updated",
        data=user.to_dict()
    )


async def delete_user(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    await db.delete(session, user)
    return DefaultResponse(
        status="success",
        message="User deleted",
        data=user.to_dict()
    )
